# -*- coding: utf-8 -*-
"""classes 蓝图：班级管理 + 班级人数统计。"""
from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import func

from auth import admin_required
from extensions import db
from models import ClassInfo, Student

bp = Blueprint("classes", __name__)


def _validate_class_form(form) -> tuple[dict, list]:
    cleaned: dict = {}
    errors: list[str] = []

    for field, label, max_len in (
        ("class_name", "班级名称", 50),
        ("major", "专业名称", 50),
        ("department", "院系名称", 50),
    ):
        value = (form.get(field) or "").strip()
        if not value:
            errors.append(f"{label}不能为空")
        elif len(value) > max_len:
            errors.append(f"{label}最长 {max_len} 个字符")
        else:
            cleaned[field] = value

    return cleaned, errors


@bp.route("/")
@admin_required
def list_classes():
    """班级列表 + 每个班的人数统计。"""
    # 用一条聚合查询算出每个班的人数，避免 N+1 次查询
    rows = (
        db.session.query(
            ClassInfo.class_id,
            ClassInfo.class_name,
            ClassInfo.major,
            ClassInfo.department,
            func.count(Student.id).label("student_count"),
        )
        .outerjoin(
            Student,
            db.and_(Student.class_id == ClassInfo.class_id, Student.is_deleted == 0),
        )
        .group_by(ClassInfo.class_id)
        .order_by(ClassInfo.class_id.asc())
        .all()
    )

    # 全校汇总
    total_students = Student.query.filter_by(is_deleted=0).count()
    unassigned = Student.query.filter_by(is_deleted=0, class_id=None).count()

    return render_template(
        "classes/list.html",
        rows=rows,
        total_students=total_students,
        unassigned=unassigned,
    )


@bp.route("/new", methods=["GET", "POST"])
@admin_required
def new_class():
    if request.method == "POST":
        data, errors = _validate_class_form(request.form)

        # 防重：同院系下班级名不能重复
        if not errors:
            dup = ClassInfo.query.filter_by(
                class_name=data["class_name"], department=data["department"]
            ).first()
            if dup is not None:
                errors.append("该院系下已存在同名班级")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("classes/form.html", cls=None, form=request.form)

        cls = ClassInfo(**data)
        db.session.add(cls)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            current_app.logger.exception("新增班级失败")
            flash("保存失败，请重试", "danger")
            return render_template("classes/form.html", cls=None, form=request.form)

        flash(f"已新增班级 {cls.class_name}", "success")
        return redirect(url_for("classes.list_classes"))

    return render_template("classes/form.html", cls=None, form={})


@bp.route("/<int:class_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_class(class_id: int):
    cls = db.session.get(ClassInfo, class_id)
    if cls is None:
        abort(404)

    if request.method == "POST":
        data, errors = _validate_class_form(request.form)

        if not errors:
            dup = ClassInfo.query.filter(
                ClassInfo.class_name == data["class_name"],
                ClassInfo.department == data["department"],
                ClassInfo.class_id != cls.class_id,
            ).first()
            if dup is not None:
                errors.append("该院系下已存在同名班级")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("classes/form.html", cls=cls, form=request.form)

        for key, value in data.items():
            setattr(cls, key, value)
        db.session.commit()

        flash(f"已更新班级 {cls.class_name}", "success")
        return redirect(url_for("classes.list_classes"))

    return render_template("classes/form.html", cls=cls, form={})


@bp.route("/<int:class_id>/delete", methods=["POST"])
@admin_required
def delete_class(class_id: int):
    cls = db.session.get(ClassInfo, class_id)
    if cls is None:
        abort(404)

    # 班级下还有学生时拒绝删除（外键是 RESTRICT，这里提前给出友好提示）
    if cls.student_count > 0:
        flash(f"班级「{cls.class_name}」下还有 {cls.student_count} 名学生，不能删除", "danger")
        return redirect(url_for("classes.list_classes"))

    db.session.delete(cls)
    db.session.commit()
    flash(f"已删除班级 {cls.class_name}", "success")
    return redirect(url_for("classes.list_classes"))
