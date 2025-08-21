"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_permission.py
@DateTime: 2025/08/21 10:42:18
@Docs: 数据模型：角色-权限 多对多中间表
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class RolePermission(BaseModel):
    """
    关系：角色-权限 多对多中间表
    """

    role = fields.ForeignKeyField(
        "models.Role", related_name="role_permissions", on_delete=fields.CASCADE, description="角色"
    )
    permission = fields.ForeignKeyField(
        "models.Permission", related_name="permission_roles", on_delete=fields.CASCADE, description="权限"
    )

    class Meta:  # type: ignore
        table = "role_permissions"
        unique_together = (("role", "permission", "is_deleted"),)
        indexes = (
            ("role",),
            ("permission",),
            ("role", "permission"),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
        )
