# -*- coding: utf-8 -*-
"""auth 蓝图：登录、登出、权限装饰器。"""
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import AdminUser, Student

bp = Blueprint("auth", __name__)


# ======================================================================
# 权限装饰器
# ======================================================================
def login_required(view):
    """未登录则跳转到登录页，并记住原本想访问的地址。"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("uid"):
            # next 参数用于登录后跳回原页面
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """必须是管理员；学生一律拒绝。"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("uid"):
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin":
            # 关键：服务端拦截，不能只靠前端隐藏按钮
            return "<h2>403 无权访问</h2><p>该页面仅管理员可用。<a href='/'>返回首页</a></p>", 403
        return view(*args, **kwargs)

    return wrapped


def super_admin_required(view):
    """必须是超级管理员。"""

    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("uid"):
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin" or not session.get("is_super"):
            return "<h2>403 无权访问</h2><p>该操作仅超级管理员可用。<a href='/'>返回首页</a></p>", 403
        return view(*args, **kwargs)

    return wrapped


def current_student() -> Student | None:
    """取当前登录的学生对象；不是学生身份则返回 None。"""
    if session.get("role") != "student":
        return None
    return Student.query.filter_by(id=session.get("uid"), is_deleted=0).first()


# ======================================================================
# 路由
# ======================================================================
@bp.route("/login", methods=["GET", "POST"])
def login():
    """统一登录入口：自动识别管理员或学生。"""
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""

        # --- 先按管理员账号查 ---
        admin = AdminUser.query.filter_by(username=username).first()
        if admin is not None and admin.is_active == 1 and admin.check_password(password):
            _clear_session()
            session["uid"] = admin.admin_id
            session["role"] = "admin"
            session["display_name"] = admin.name
            session["is_super"] = admin.is_super
            flash(f"欢迎回来，{admin.name}", "success")
            return _safe_redirect()

        # --- 再按学号登录学生（易班对接前的过渡方案）---
        student = Student.query.filter_by(
            student_no=username, is_deleted=0
        ).first()
        # 学生暂时用"手机号后 6 位"作为初始密码，或由管理员设置
        if student is not None and password == _student_password(student):
            _clear_session()
            session["uid"] = student.id
            session["role"] = "student"
            session["display_name"] = student.name
            session["is_super"] = False
            flash(f"欢迎回来，{student.name}", "success")
            return _safe_redirect()

        # 统一提示，不透露"账号存在但密码错"这类信息（防账号枚举）
        flash("账号或密码错误", "danger")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """退出登录：彻底清空 Session。"""
    _clear_session()
    flash("已退出登录", "info")
    return redirect(url_for("auth.login"))


# ======================================================================
# 内部辅助
# ======================================================================
def _clear_session() -> None:
    """清理登录相关键。"""
    for key in ("uid", "role", "display_name", "is_super"):
        session.pop(key, None)


def _student_password(student: Student) -> str:
    """
    学生初始密码规则：手机号后 6 位；没有手机号则用学号后 6 位。
    真实项目应改为易班登录，不让学生记密码。
    """
    if student.phone and len(student.phone) >= 6:
        return student.phone[-6:]
    return (student.student_no or "")[-6:]


def _safe_redirect():
    """
    跳转前校验 next 参数，只允许站内相对路径。
    否则攻击者可构造 /login?next=https://evil.com 做钓鱼跳转。
    """
    target = request.args.get("next") or ""
    if target.startswith("/") and not target.startswith("//"):
        return redirect(target)
    return redirect(url_for("index"))
