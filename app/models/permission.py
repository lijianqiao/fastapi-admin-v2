"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permission.py
@DateTime: 2025/08/21 10:19:39
@Docs: 数据模型：权限
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class Permission(BaseModel):
    """
    数据模型：权限
    """

    code = fields.CharField(max_length=64, index=True, description="权限编码（唯一，如 user:list）")
    name = fields.CharField(max_length=64, description="权限名称（展示用）")
    description = fields.CharField(max_length=255, null=True, description="权限描述")

    class Meta:  # type: ignore
        table = "permissions"
        unique_together = (
            ("code", "is_deleted"),
            ("name", "is_deleted"),
        )
        indexes = (
            ("code",),
            ("name",),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
        )
