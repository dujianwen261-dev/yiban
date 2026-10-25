# -*- coding: utf-8 -*-
"""
初始化脚本（只需运行一次）
==========================
作用：
  1. 创建数据库 student_manage（如果不存在）
  2. 创建所有表
  3. 创建超级管理员账号
  4. 插入示例班级和示例学生（方便你立刻看到效果）

运行：
  python init_db.py

重复运行是安全的：已存在的表和账号会被跳过，不会覆盖你的数据。
"""
import os
import sys

import pymysql
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), ".env"))


def parse_db_url(url: str) -> dict:
    """从 SQLAlchemy 连接串里取出连接信息。"""
    # 例：mysql+pymysql://root:pass@127.0.0.1:3306/student_manage?charset=utf8mb4
    rest = url.split("://", 1)[1]
    credentials, hostpart = rest.rsplit("@", 1)
    user, password = credentials.split(":", 1)
    hostport, _, dbpart = hostpart.partition("/")
    host, _, port = hostport.partition(":")
    dbname = dbpart.split("?", 1)[0]
    return {
        "user": user,
        "password": password,
        "host": host or "127.0.0.1",
        "port": int(port or 3306),
        "database": dbname,
    }


def ensure_database(info: dict) -> None:
    """连接 MySQL 服务器（不指定库），创建目标库。"""
    conn = pymysql.connect(
        host=info["host"],
        port=info["port"],
        user=info["user"],
        password=info["password"],
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{info['database']}` "
                f"DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        print(f"[1/4] 数据库 `{info['database']}` 已就绪")
    finally:
        conn.close()


def main() -> int:
    url = os.environ.get("DATABASE_URL", "")
    if not url.startswith("mysql"):
        print("错误：DATABASE_URL 未正确配置，请检查 .env")
        return 1

    info = parse_db_url(url)
    ensure_database(info)

    # 必须在设置好环境后再导入应用，确保读到正确的配置
    from app import create_app
    from extensions import db
    from models import AdminUser, ClassInfo, Student

    app = create_app()

    with app.app_context():
        # ---- 建表 ----
        db.create_all()
        print("[2/4] 所有表已创建")

        # ---- 超级管理员 ----
        admin = AdminUser.query.filter_by(username="admin").first()
        if admin is None:
            admin = AdminUser(username="admin", name="系统管理员", role="超级管理员")
            admin.set_password("Admin@123456")
            db.session.add(admin)
            db.session.commit()
            print("[3/4] 已创建超级管理员：admin / Admin@123456  ← 请登录后立刻修改")
        else:
            print("[3/4] 超级管理员 admin 已存在，跳过")

        # ---- 示例数据 ----
        if ClassInfo.query.count() == 0:
            c1 = ClassInfo(
                class_name="计算机 2401 班",
                major="计算机科学与技术",
                department="信息工程学院",
            )
            c2 = ClassInfo(
                class_name="软件 2402 班",
                major="软件工程",
                department="信息工程学院",
            )
            db.session.add_all([c1, c2])
            db.session.commit()

            students = [
                Student(
                    student_no="2024010101", name="张伟", gender="男",
                    class_id=c1.class_id, phone="13800000001",
                    email="zhangwei@example.com", address="示例省示例市",
                ),
                Student(
                    student_no="2024010102", name="李娜", gender="女",
                    class_id=c1.class_id, phone="13800000002",
                    email="lina@example.com", address="示例省示例市",
                ),
                Student(
                    student_no="2024010201", name="王强", gender="男",
                    class_id=c2.class_id, phone="13800000003",
                    email="wangqiang@example.com", address="示例省示例市",
                ),
            ]
            db.session.add_all(students)
            db.session.commit()
            print("[4/4] 已插入 2 个班级、3 名学生")
            print("      学生登录示例：学号 2024010101，密码 000001（手机号后 6 位）")
        else:
            print("[4/4] 已有数据，跳过示例数据插入")

    print("\n初始化完成。运行 python app.py 启动系统。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
