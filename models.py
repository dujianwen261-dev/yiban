# -*- coding: utf-8 -*-
"""
数据模型模块
============
一张表 = 一个类，一行数据 = 一个实例，一个字段 = 一个 db.Column。

设计要点（对比最初方案做的修正）：
1. 学生表用自增 id 做代理主键，学号只做"唯一约束"
   —— 学号录错时只改字段，不会牵连外键。
2. 手机号/邮箱/住址允许学生自己改；姓名/学号/班级只能管理员改。
3. 密码字段必须 VARCHAR(255)，因为安全哈希长约 162 字符。
4. 软删除：标记 is_deleted 而不是真删，误删可恢复。
5. 所有表 utf8mb4，能存 emoji 和生僻字。
"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db


class ClassInfo(db.Model):
    """班级表：一个班级有多名学生（一对多）。"""

    __tablename__ = "class_info"

    class_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    class_name = db.Column(db.String(50), nullable=False)
    major = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # 反向关系：通过班级对象直接访问学生列表
    #   1. backref="class_info" 会在 Student 上生成 .class_info 属性
    #   2. lazy="select" 表示访问时才发查询
    #   3. cascade 让删除班级时行为可控（这里用 passive_deletes 交给外键约束）
    students = db.relationship(
        "Student",
        backref="class_info",
        lazy="select",
        passive_deletes=True,
    )

    @property
    def student_count(self) -> int:
        """该班级下未删除的学生人数。"""
        return Student.query.filter_by(class_id=self.class_id, is_deleted=0).count()

    def __repr__(self) -> str:
        return f"<ClassInfo {self.class_id} {self.class_name}>"


class Student(db.Model):
    """学生表。"""

    __tablename__ = "student_info"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)          # 代理主键
    student_no = db.Column(db.String(20), nullable=False, unique=True)        # 学号
    name = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(4), nullable=True)
    class_id = db.Column(
        db.Integer,
        db.ForeignKey("class_info.class_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=True,
    )
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    enroll_date = db.Column(db.Date, nullable=True)

    # 易班登录映射：通过易班 userid 找到这名学生
    yiban_uid = db.Column(db.String(32), nullable=True, unique=True)

    # 软删除标记：0 正常 / 1 已删除
    is_deleted = db.Column(db.SmallInteger, nullable=False, default=0)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )

    # 复合索引：列表页按 class_id 过滤 + is_deleted 过滤是最常见查询
    __table_args__ = (
        db.Index("idx_student_name", "name"),
        db.Index("idx_student_class_deleted", "class_id", "is_deleted"),
    )

    def __repr__(self) -> str:
        return f"<Student {self.student_no} {self.name}>"


class AdminUser(db.Model):
    """管理员表（含超级管理员）。"""

    __tablename__ = "admin_user"

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    # 关键：255，不是 32。安全哈希长约 162 字符，32 会被截断导致永远验证失败
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(20), nullable=False)

    # 让管理员也能被易班识别（最初方案缺了这列，导致"学号在不在管理员表"无法实现）
    yiban_uid = db.Column(db.String(32), nullable=True, unique=True)

    role = db.Column(db.String(20), nullable=False, default="普通管理员")
    is_active = db.Column(db.SmallInteger, nullable=False, default=1)   # 1 启用 / 0 禁用
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # ------------------------------------------------------------------
    # 密码处理：只存哈希，永不存明文
    # ------------------------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        """把明文密码转成哈希后存入 self.password。"""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """校验明文密码是否正确。"""
        if not self.password:
            return False
        return check_password_hash(self.password, raw_password)

    @property
    def is_super(self) -> bool:
        return self.role == "超级管理员"

    def __repr__(self) -> str:
        return f"<AdminUser {self.username} {self.role}>"
