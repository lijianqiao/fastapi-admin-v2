"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 10:19:49
@Docs: 数据模型：角色
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class Role(BaseModel):
    """
    数据模型：角色
    """

    name = fields.CharField(max_length=64, description="角色名称（唯一）")
    code = fields.CharField(max_length=64, index=True, description="角色编码（唯一）")
    description = fields.CharField(max_length=255, null=True, description="角色描述")

    class Meta:  # type: ignore
        table = "roles"
        unique_together = (
            ("name", "is_deleted"),
            ("code", "is_deleted"),
        )
        indexes = (
            ("name",),
            ("code",),
            ("id", "version"),
            ("is_active", "is_deleted"),
            ("created_at",),
            ("updated_at",),
        )
