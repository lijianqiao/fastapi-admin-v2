"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: config.py
@DateTime: 2025/08/21 09:43:58
@Docs: 应用配置
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置

    Args:
        BaseSettings (_type_): _description_

    Returns:
        Settings: 应用配置
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # 应用
    APP_NAME: str = Field(default="FastAPIAdmin")
    APP_VERSION: str = Field(default="0.1.0")
    APP_DESCRIPTION: str = Field(default="基于FastAPI的后台管理系统")
    API_PREFIX: str = Field(default="/api")
    DEBUG: bool = Field(default=True)
    ENVIRONMENT: str = Field(default="development")
    # 日志
    APP_LOG_PATH: str | None = Field(default=None)

    # 服务器
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # 数据库（PostgreSQL, asyncpg 驱动）
    DATABASE_URL: str = Field(default="postgres://postgres:postgres@localhost:5432/fastapi_admin")

    # Redis
    # 示例：redis://localhost:6379/0
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # 安全配置
    JWT_SECRET_KEY: str = Field(default="change-me-secret")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = Field(default=60 * 30)  # 30分钟
    REFRESH_TOKEN_EXPIRE_SECONDS: int = Field(default=60 * 60 * 24 * 7)  # 7天

    # 登录安全策略
    LOGIN_MAX_FAILED_ATTEMPTS: int = Field(default=5)
    LOGIN_LOCK_MINUTES: int = Field(default=3)  # 锁定3分钟，避免暴力破解

    # 超级管理员配置
    SUPERUSER_USERNAME: str = Field(default="admin")
    SUPERUSER_PASSWORD: str = Field(default="admin@123")
    SUPERUSER_EMAIL: str = Field(default="admin@example.com")
    SUPERUSER_PHONE: str = Field(default="13800000000")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """获取应用配置

    Returns:
        Settings: 应用配置
    """
    return Settings()
