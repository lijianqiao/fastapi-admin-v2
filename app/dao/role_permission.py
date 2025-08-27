"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role_permission.py
@DateTime: 2025/08/21 11:05:00
@Docs: 角色-权限关系 DAO
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from tortoise.transactions import in_transaction

from app.dao.base import BaseDAO
from app.models import RolePermission


class RolePermissionDAO(BaseDAO[RolePermission]):
    """角色-权限关系数据访问对象。"""

    def __init__(self) -> None:
        super().__init__(RolePermission)

    async def bind_permissions(self, role_id: int, permission_ids: Sequence[int]) -> dict[str, int]:
        """为单个角色绑定多个权限。

        Args:
            role_id (int): 角色ID。
            permission_ids (Sequence[int]): 权限ID集合。

        Returns:
            None: 无返回。
        """
        if not permission_ids:
            return {"added": 0, "restored": 0, "existed": 0}
        # 去重并恢复软删
        existing = await self.model.filter(role_id=role_id, permission_id__in=list(permission_ids)).all()
        restore_ids: list[int] = [int(x.id) for x in existing if getattr(x, "is_deleted", False)]
        existed_active: set[int] = {x.permission_id for x in existing if not getattr(x, "is_deleted", False)}  # type: ignore[attr-defined]
        to_create = [
            pid
            for pid in permission_ids
            if pid not in existed_active and all(x.permission_id != pid for x in existing)  # type: ignore[attr-defined]
        ]
        now = datetime.now(tz=UTC)
        added = 0
        restored = 0
        existed = len(existed_active)
        async with in_transaction():
            if restore_ids:
                await self.model.filter(id__in=restore_ids).update(is_deleted=False, updated_at=now)
                restored = len(restore_ids)
            if to_create:
                rows = [{"role_id": role_id, "permission_id": pid} for pid in to_create]
                await self.bulk_create(rows)
                added = len(to_create)
        return {"added": added, "restored": restored, "existed": existed}

    async def unbind_permissions(self, role_id: int, permission_ids: Sequence[int]) -> int:
        """为单个角色移除多个权限。

        Args:
            role_id (int): 角色ID。
            permission_ids (Sequence[int]): 权限ID集合。

        Returns:
            int: 受影响行数。
        """

        now = datetime.now(tz=UTC)
        async with in_transaction():
            return (
                await self.alive()
                .filter(role_id=role_id, permission_id__in=list(permission_ids))
                .update(is_deleted=True, updated_at=now)
            )

    async def list_permissions_of_role(self, role_id: int) -> list[RolePermission]:
        """查询单个角色的权限关系列表。

        Args:
            role_id (int): 角色ID。

        Returns:
            list[RolePermission]: 权限关系列表。
        """
        return await self.alive().filter(role_id=role_id).all()

    async def list_by_role_ids(self, role_ids: Sequence[int]) -> list[RolePermission]:
        """按角色ID集合查询权限关系列表。

        Args:
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            list[RolePermission]: 权限关系列表。
        """
        if not role_ids:
            return []
        return await self.alive().filter(role_id__in=list(role_ids)).all()

    async def list_roles_of_permission(self, permission_id: int) -> list[RolePermission]:
        """查询某权限下的角色关系列表。

        Args:
            permission_id (int): 权限ID。

        Returns:
            list[RolePermission]: 角色关系列表。
        """
        return await self.alive().filter(permission_id=permission_id).all()

    async def bind_permissions_to_roles(self, role_ids: Sequence[int], permission_ids: Sequence[int]) -> dict[str, int]:
        """为多个角色批量绑定多个权限。

        Args:
            role_ids (Sequence[int]): 角色ID集合。
            permission_ids (Sequence[int]): 权限ID集合。

        Returns:
            None: 无返回。
        """
        if not role_ids or not permission_ids:
            return {"added": 0, "restored": 0, "existed": 0}
        targets = [(rid, pid) for rid in role_ids for pid in permission_ids]
        existing = await self.model.filter(role_id__in=list(role_ids), permission_id__in=list(permission_ids)).all()
        exist_map: dict[tuple[int, int], tuple[int, bool]] = {}
        for x in existing:
            exist_map[(x.role_id, x.permission_id)] = (int(x.id), bool(getattr(x, "is_deleted", False)))  # type: ignore[attr-defined]
        to_restore_ids: list[int] = []
        to_create_rows: list[dict[str, int]] = []
        for rid, pid in targets:
            hit = exist_map.get((rid, pid))
            if hit is None:
                to_create_rows.append({"role_id": rid, "permission_id": pid})
            else:
                row_id, was_deleted = hit
                if was_deleted:
                    to_restore_ids.append(row_id)
        now = datetime.now(tz=UTC)
        added = 0
        restored = 0
        existed = 0
        for _, was_deleted in exist_map.values():
            if was_deleted:
                restored += 1
            else:
                existed += 1
        async with in_transaction():
            if to_restore_ids:
                await self.model.filter(id__in=to_restore_ids).update(is_deleted=False, updated_at=now)
                restored = len(to_restore_ids)
            if to_create_rows:
                await self.bulk_create(to_create_rows)
                added = len(to_create_rows)
        return {"added": added, "restored": restored, "existed": existed}

    async def unbind_permissions_from_roles(self, role_ids: Sequence[int], permission_ids: Sequence[int]) -> int:
        """为多个角色批量移除多个权限。

        Args:
            role_ids (Sequence[int]): 角色ID集合。
            permission_ids (Sequence[int]): 权限ID集合。

        Returns:
            int: 受影响行数。
        """

        now = datetime.now(tz=UTC)
        async with in_transaction():
            return (
                await self.alive()
                .filter(role_id__in=list(role_ids), permission_id__in=list(permission_ids))
                .update(is_deleted=True, updated_at=now)
            )
