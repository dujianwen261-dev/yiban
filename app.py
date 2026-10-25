# -*- coding: utf-8 -*-
"""
应用入口（应用工厂模式）
========================
为什么用 create_app() 函数而不是直接写 app = Flask(__name__)？

1. 避免循环导入：auth/models 要导入 app 里的东西，工厂函数能推迟绑定时机。
2. 方便测试：测试时用不同配置创建独立 app 实例，互不污染。
3. 这是 Flask 官方推荐写法，后续加功能不会推倒重来。

运行方式（三选一）：
    python app.py
    flask --app app run --debug
    flask --app app:create_app run --debug
"""
import os

from flask import Flask, redirect, session, url_for

from config import get_config
from extensions import db


def create_app(config_name: str | None = None) -> Flask:
    """创建并配置 Flask 应用实例。"""
    app = Flask(__name__)

    # 1) 加载配置
    app.config.from_object(get_config(config_name))

    # 2) 初始化扩展
    db.init_app(app)

    # 3) 注册蓝图（每个蓝图 = 一个功能模块）
    from auth import bp as auth_bp
    from classes import bp as classes_bp
    from students import bp as students_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(classes_bp, url_prefix="/classes")

    # 4) 首页：按登录身份跳转
    @app.route("/")
    def index():
        if not session.get("uid"):
            return redirect(url_for("auth.login"))
        if session.get("role") == "student":
            return redirect(url_for("students.me"))
        return redirect(url_for("students.list_students"))

    # 5) 统一错误页：不把内部堆栈暴露给用户
    @app.errorhandler(404)
    def not_found(_error):
        return "<h2>404 页面不存在</h2><p><a href='/'>返回首页</a></p>", 404

    @app.errorhandler(500)
    def server_error(_error):
        db.session.rollback()
        return "<h2>500 服务器内部错误</h2><p>请联系管理员</p>", 500

    return app


app = create_app()


if __name__ == "__main__":
    # 兜底：首次启动自动建表（只建缺失的表，不会删已有数据）
    with app.app_context():
        db.create_all()

    debug = os.environ.get("APP_ENV", "development") != "production"
    app.run(host="127.0.0.1", port=5000, debug=debug)
