# -*- coding: utf-8 -*-
"""students 蓝图：学生信息增删改查、分页查询、学生自查自改。"""
import re
from datetime import date, datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import or_

from auth import admin_required, current_student, login_required
from extensions import db
from models import ClassInfo, Student

bp = Blueprint("students", __name__)

# 白名单：学生只能改这几个字段。
# 用白名单而不是"排除法"，新增敏感字段时才不会漏防护。
STUDENT_EDITABLE_FIELDS = ("phone", "email", "address")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^1[3-9]\d{9}$")


# ======================================================================
# 工具函数
# ======================================================================
def _validate_student_form(form) -> tuple[dict, list]:
    """校验并规整表单数据。返回 (清洗后的字段字典, 错误列表)。"""
    cleaned: dict = {}
    errors: list[str] = []

    student_no = (form.get("student_no") or "").strip()
    name = (form.get("name") or "").strip()
    gender = (form.get("gender") or "").strip()
    class_id_raw = (form.get("class_id") or "").strip()
    phone = (form.get("phone") or "").strip()
    email = (form.get("email") or "").strip()
    address = (form.get("address") or "").strip()
    enroll_raw = (form.get("enroll_date") or "").strip()

    if not student_no:
        errors.append("学号不能为空")
    elif len(student_no) > 20:
        errors.append("学号最长 20 个字符")
    else:
        cleaned["student_no"] = student_no

    if not name:
        errors.append("姓名不能为空")
    elif len(name) > 20:
        errors.append("姓名最长 20 个字符")
    else:
        cleaned["name"] = name

    if gender:
        if gender not in ("男", "女"):
            errors.append("性别只能是 男 或 女")
        else:
            cleaned["gender"] = gender
    else:
        cleaned["gender"] = None

    if class_id_raw:
        if not class_id_raw.isdigit():
            errors.append("班级参数非法")
        else:
            cid = int(class_id_raw)
            if db.session.get(ClassInfo, cid) is None:
                errors.append("所选班级不存在")
            else:
                cleaned["class_id"] = cid
    else:
        cleaned["class_id"] = None

    if phone:
        if not PHONE_RE.match(phone):
            errors.append("手机号格式不正确（应为 11 位大陆手机号）")
        else:
            cleaned["phone"] = phone
    else:
        cleaned["phone"] = None

    if email:
        if not EMAIL_RE.match(email) or len(email) > 50:
            errors.append("邮箱格式不正确")
        else:
            cleaned["email"] = email
    else:
        cleaned["email"] = None

    cleaned["address"] = address[:200] if address else None

    if enroll_raw:
        try:
            cleaned["enroll_date"] = datetime.strptime(enroll_raw, "%Y-%m-%d").date()
        except ValueError:
            errors.append("入学日期格式应为 YYYY-MM-DD")
    else:
        cleaned["enroll_date"] = None

    return cleaned, errors


def _get_student_or_404(student_id: int) -> Student:
    """取未删除的学生，不存在则 404。"""
    student = Student.query.filter_by(id=student_id, is_deleted=0).first()
    if student is None:
        abort(404)
    return student


def _apply_student_fields(student: Student, data: dict) -> None:
    """把清洗后的数据写到模型对象上。"""
    for key, value in data.items():
        setattr(student, key, value)


# ======================================================================
# 管理员：学生列表（含模糊查询 + 分页）
# ======================================================================
@bp.route("/")
@admin_required
def list_students():
    keyword = (request.args.get("q") or "").strip()
    class_filter = (request.args.get("class_id") or "").strip()

    # 注意：这里全部走 SQLAlchemy 的表达式，不存在 SQL 字符串拼接，
    # 因此天然免疫 SQL 注入（q 里写 ' OR 1=1 -- 也只会被当普通文本）
    query = Student.query.filter(Student.is_deleted == 0)

    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Student.student_no.like(like),
                Student.name.like(like),
                Student.phone.like(like),
            )
        )

    if class_filter.isdigit():
        query = query.filter(Student.class_id == int(class_filter))

    query = query.order_by(Student.student_no.asc())

    page = request.args.get("page", 1, type=int)
    page = max(page, 1)
    pagination = query.paginate(
        page=page,
        per_page=current_app.config["PAGE_SIZE"],
        error_out=False,
    )

    classes = ClassInfo.query.order_by(ClassInfo.class_id.asc()).all()

    return render_template(
        "students/list.html",
        pagination=pagination,
        students=pagination.items,
        classes=classes,
        keyword=keyword,
        class_filter=class_filter,
    )


# ======================================================================
# 管理员：新增学生
# ======================================================================
@bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_student():
    classes = ClassInfo.query.order_by(ClassInfo.class_id.asc()).all()

    if request.method == "POST":
        data, errors = _validate_student_form(request.form)

        if not errors:
            # 学号唯一性检查（软删除的也算占用，避免历史学号被复用）
            exists = Student.query.filter_by(student_no=data.get("student_no")).first()
            if exists is not None:
                errors.append(f"学号 {data['student_no']} 已存在")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template(
                "students/form.html",
                student=None,
                classes=classes,
                form=request.form,
            )

        student = Student()
        _apply_student_fields(student, data)
        db.session.add(student)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("新增学生失败")
            flash("保存失败，请检查数据后重试", "danger")
            return render_template(
                "students/form.html", student=None, classes=classes, form=request.form
            )

        flash(f"已新增学生 {student.name}", "success")
        # PRG 模式：POST 成功后重定向，避免刷新页面重复提交
        return redirect(url_for("students.list_students"))

    return render_template(
        "students/form.html", student=None, classes=classes, form={}
    )


# ======================================================================
# 管理员：修改学生
# ======================================================================
@bp.route("/<int:student_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_student(student_id: int):
    student = _get_student_or_404(student_id)
    classes = ClassInfo.query.order_by(ClassInfo.class_id.asc()).all()

    if request.method == "POST":
        data, errors = _validate_student_form(request.form)

        if not errors:
            new_no = data.get("student_no")
            clash = Student.query.filter(
                Student.student_no == new_no, Student.id != student.id
            ).first()
            if clash is not None:
                errors.append(f"学号 {new_no} 已被其他学生占用")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template(
                "students/form.html", student=student, classes=classes, form=request.form
            )

        _apply_student_fields(student, data)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("修改学生失败")
            flash("保存失败，请检查数据后重试", "danger")
            return render_template(
                "students/form.html", student=student, classes=classes, form=request.form
            )

        flash(f"已更新学生 {student.name}", "success")
        return redirect(url_for("students.list_students"))

    return render_template(
        "students/form.html", student=student, classes=classes, form={}
    )


# ======================================================================
# 管理员：删除学生（软删除）
# ======================================================================
@bp.route("/<int:student_id>/delete", methods=["POST"])
@admin_required
def delete_student(student_id: int):
    student = _get_student_or_404(student_id)

    # 用 POST 而不是 GET：GET 可被 <img src> 之类跨站触发
    student.is_deleted = 1
    db.session.commit()

    flash(f"已删除学生 {student.name}（可通过数据库恢复）", "success")
    return redirect(url_for("students.list_students"))


# ======================================================================
# 学生：查看自己的信息
# ======================================================================
@bp.route("/me")
@login_required
def me():
    student = current_student()
    if student is None:
        flash("当前账号不是学生身份", "warning")
        return redirect(url_for("index"))

    # 只把自己的数据传给模板，页面上根本不存在别人的数据
    return render_template("students/me.html", student=student)


# ======================================================================
# 学生：修改自己的信息（只能改白名单字段）
# ======================================================================
@bp.route("/me/edit", methods=["GET", "POST"])
@login_required
def edit_me():
    student = current_student()
    if student is None:
        flash("当前账号不是学生身份", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        errors: list[str] = []
        phone = (request.form.get("phone") or "").strip()
        email = (request.form.get("email") or "").strip()
        address = (request.form.get("address") or "").strip()

        if phone and not PHONE_RE.match(phone):
            errors.append("手机号格式不正确（应为 11 位大陆手机号）")
        if email and (not EMAIL_RE.match(email) or len(email) > 50):
            errors.append("邮箱格式不正确")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("students/me_form.html", student=student)

        # 只赋值白名单字段；即使请求里伪造了 student_no，这里也读不到
        student.phone = phone or None
        student.email = email or None
        student.address = address[:200] if address else None
        db.session.commit()

        flash("个人信息已更新", "success")
        return redirect(url_for("students.me"))

    return render_template("students/me_form.html", student=student)
