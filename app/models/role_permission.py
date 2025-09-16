"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_permission.py
@DateTime: 2025/08/21 10:42:18
@Docs: 数据模型：角色-权限 多对多中间表
"""

from tortoise import fields

from app.models.base import BaseModel


class RolePermission(BaseModel):
    """角色-权限关系实体（多对多中间表）。

    表示角色与权限的绑定关系，用于计算角色的权限集。

    Attributes:
        role (Role): 关联角色。
        permission (Permission): 关联权限。

    Constraints:
        - 软删唯一：(`role`, `permission`, `is_deleted`)。
        - 常用索引：role、permission、(role, permission)、(id, version)、(is_active, is_deleted)。
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
