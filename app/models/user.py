"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 10:19:58
@Docs: 数据模型：用户
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class User(BaseModel):
    """
    数据模型：用户
    """

    username = fields.CharField(max_length=64, index=True, description="用户名（唯一）")
    phone = fields.CharField(max_length=20, index=True, description="手机号（唯一，必填）")
    email = fields.CharField(max_length=128, null=True, index=True, description="邮箱（可选，唯一）")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    failed_attempts = fields.IntField(default=0, description="连续登录失败次数")
    locked_until = fields.DatetimeField(null=True, description="账户锁定截止时间")
    last_login_at = fields.DatetimeField(null=True, description="最近登录时间")

    class Meta:  # type: ignore
        table = "users"
        unique_together = (
            ("username", "is_deleted"),
            ("phone", "is_deleted"),
            ("email", "is_deleted"),
        )
        indexes = (
            ("username",),
            ("phone",),
            ("email",),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
            ("last_login_at",),
        )
