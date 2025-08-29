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
    """用户实体。

    表示系统中的用户账号与状态信息。

    Attributes:
        username (str): 用户名（唯一，索引）。
        phone (str): 手机号（唯一，必填，索引）。
        email (str | None): 邮箱（唯一，必填，索引）。
        password_hash (str): 密码哈希。
        failed_attempts (int): 连续登录失败次数。
        locked_until (datetime | None): 账户锁定截止时间。
        last_login_at (datetime | None): 最近登录时间。

    Constraints:
        - 软删唯一：(`username`, `is_deleted`)、(`phone`, `is_deleted`)、(`email`, `is_deleted`)。
        - 常用查询索引：用户名、手机号、邮箱、(id, version)、(is_active, is_deleted) 等。
    """

    username = fields.CharField(max_length=64, unique=True, db_index=True, description="用户名（唯一）")
    phone = fields.CharField(max_length=20, unique=True, db_index=True, description="手机号（唯一，必填）")
    email = fields.CharField(max_length=128, unique=True, db_index=True, description="邮箱（唯一，必填）")
    nickname = fields.CharField(max_length=64, unique=True, db_index=True, description="昵称（唯一，必填）")
    bio = fields.TextField(null=True, description="简介（可选）")
    avatar_url = fields.CharField(max_length=255, null=True, description="头像URL（可选）")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    failed_attempts = fields.IntField(default=0, description="连续登录失败次数")
    locked_until = fields.DatetimeField(null=True, description="账户锁定截止时间")
    last_login_at = fields.DatetimeField(null=True, description="最近登录时间")

    class Meta:  # type: ignore
        table = "users"
        indexes = (
            ("username",),
            ("phone",),
            ("email",),
            ("nickname",),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
            ("last_login_at",),
        )
