"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_permission.py
@DateTime: 2025/08/21 11:05:00
@Docs: 角色-权限关系 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from app.dao.base import BaseDAO
from app.models import RolePermission


class RolePermissionDAO(BaseDAO[RolePermission]):
    """角色-权限关系数据访问对象。"""

    def __init__(self) -> None:
        super().__init__(RolePermission)

    async def bind_permissions(self, role_id: int, permission_ids: Sequence[int]) -> None:
        """为单个角色绑定多个权限。"""
        rows = [{"role_id": role_id, "permission_id": pid} for pid in permission_ids]
        await self.bulk_create(rows)

    async def unbind_permissions(self, role_id: int, permission_ids: Sequence[int]) -> int:
        """为单个角色移除多个权限。

        Returns:
            int: 受影响行数。
        """
        return (
            await self.alive().filter(role_id=role_id, permission_id__in=list(permission_ids)).update(is_deleted=True)
        )

    async def list_permissions_of_role(self, role_id: int) -> list[RolePermission]:
        """查询单个角色的权限关系列表。"""
        return await self.alive().filter(role_id=role_id).all()

    async def list_by_role_ids(self, role_ids: Sequence[int]) -> list[RolePermission]:
        """按角色ID集合查询权限关系列表。"""
        if not role_ids:
            return []
        return await self.alive().filter(role_id__in=list(role_ids)).all()

    async def bind_permissions_to_roles(self, role_ids: Sequence[int], permission_ids: Sequence[int]) -> None:
        """为多个角色批量绑定多个权限。"""
        rows = [{"role_id": rid, "permission_id": pid} for rid in role_ids for pid in permission_ids]
        if rows:
            await self.bulk_create(rows)

    async def unbind_permissions_from_roles(self, role_ids: Sequence[int], permission_ids: Sequence[int]) -> int:
        """为多个角色批量移除多个权限。

        Returns:
            int: 受影响行数。
        """
        return (
            await self.alive()
            .filter(role_id__in=list(role_ids), permission_id__in=list(permission_ids))
            .update(is_deleted=True)
        )
