# -*- coding: utf-8 -*-
"""
配置模块
========
所有"可变的、敏感的"参数都集中在这里，并从环境变量或 .env 读取。
原则：密码、密钥绝不能硬编码进源码，否则会跟着 Git 传到公开仓库。
"""
import os

from dotenv import load_dotenv

# 加载项目根目录下的 .env 文件（不存在也不会报错）
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))


class Config:
    """基础配置：所有环境共用。"""

    # ------------------------------------------------------------------
    # 安全相关
    # ------------------------------------------------------------------
    # Flask 用它来给 Session Cookie 签名。
    # 如果为空或可预测，攻击者就能伪造别人的登录状态。
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-only-insecure-key-change-me"

    # Session Cookie 的安全属性
    SESSION_COOKIE_HTTPONLY = True   # 禁止 JavaScript 读取 Cookie（防 XSS 偷 Session）
    SESSION_COOKIE_SAMESITE = "Lax"  # 防 CSRF 的第一道防线
    # 本地用 http 调试时必须为 False；上线换 HTTPS 后要改成 True
    SESSION_COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"

    # ------------------------------------------------------------------
    # 数据库相关
    # ------------------------------------------------------------------
    # 注意驱动前缀：mysql+pymysql 表示"用 MySQL 方言 + pymysql 驱动"。
    # 只写 mysql:// 会去找 MySQLdb，环境里没有就会报 ModuleNotFoundError。
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "mysql+pymysql://root:abcd2005@127.0.0.1:3306/student_manage?charset=utf8mb4",
    )

    # 连接池健康检查：防止 MySQL 8 小时空闲断连后，第一个请求拿到死连接报错
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # ------------------------------------------------------------------
    # 业务参数
    # ------------------------------------------------------------------
    PAGE_SIZE = 10          # 学生列表每页条数
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024   # 请求体上限 8MB


class DevelopmentConfig(Config):
    """开发环境：开启调试。"""

    DEBUG = True
    SESSION_COOKIE_SECURE = False   # 本地 http 必须关闭


class ProductionConfig(Config):
    """生产环境：关调试、强制安全 Cookie。"""

    DEBUG = False
    SESSION_COOKIE_SECURE = True


# 通过环境变量 FLASK_ENV / APP_ENV 选择配置类
config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(name: str | None = None):
    """按名字取配置类，默认取 development。"""
    key = name or os.environ.get("APP_ENV") or "default"
    return config_map.get(key, config_map["default"])
