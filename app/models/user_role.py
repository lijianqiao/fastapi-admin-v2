"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_role.py
@DateTime: 2025/08/21 10:44:15
@Docs: 数据模型：用户-角色 多对多中间表
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class UserRole(BaseModel):
    """
    关系：用户-角色 多对多中间表
    """

    user = fields.ForeignKeyField(
        "models.User", related_name="user_roles", on_delete=fields.CASCADE, description="用户"
    )
    role = fields.ForeignKeyField(
        "models.Role", related_name="role_users", on_delete=fields.CASCADE, description="角色"
    )

    class Meta:  # type: ignore
        table = "user_roles"
        unique_together = (("user", "role", "is_deleted"),)
        indexes = (
            ("user",),
            ("role",),
            ("user", "role"),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
        )
