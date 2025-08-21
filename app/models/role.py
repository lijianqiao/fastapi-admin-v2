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
    """角色实体。

    用于聚合权限并赋予用户，实现基于角色的访问控制（RBAC）。

    Attributes:
        name (str): 角色名称（唯一）。
        code (str): 角色编码（唯一，索引），推荐小写下划线或短横线风格。
        description (str | None): 角色描述。

    Constraints:
        - 软删唯一：(`name`, `is_deleted`)、(`code`, `is_deleted`)。
        - 常用索引：name、code、(id, version)、(is_active, is_deleted)。
    """

    name = fields.CharField(max_length=64, description="角色名称（唯一）")
    code = fields.CharField(max_length=64, db_index=True, description="角色编码（唯一）")
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
