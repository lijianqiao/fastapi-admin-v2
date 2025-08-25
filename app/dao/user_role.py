"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_role.py
@DateTime: 2025/08/21 11:05:00
@Docs: 用户-角色关系 DAO
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from tortoise.transactions import in_transaction

from app.dao.base import BaseDAO
from app.models import UserRole


class UserRoleDAO(BaseDAO[UserRole]):
    """用户-角色关系数据访问对象。"""

    def __init__(self) -> None:
        super().__init__(UserRole)

    async def bind_roles(self, user_id: int, role_ids: Sequence[int]) -> dict[str, int]:
        """为单个用户绑定多个角色。

        Args:
            user_id (int): 用户ID。
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            None: 无返回。
        """
        if not role_ids:
            return {"added": 0, "restored": 0, "existed": 0}
        # 查已有（包含软删），避免重复写入；软删则恢复
        existing = await self.model.filter(user_id=user_id, role_id__in=list(role_ids)).all()
        restore_ids: list[int] = [int(x.id) for x in existing if getattr(x, "is_deleted", False)]
        existed_active: set[int] = {int(x.role.id) for x in existing if not getattr(x, "is_deleted", False)}
        to_create = [
            rid for rid in role_ids if rid not in existed_active and all(int(x.role.id) != rid for x in existing)
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
                rows = [{"user_id": user_id, "role_id": rid} for rid in to_create]
                await self.bulk_create(rows)
                added = len(to_create)
        return {"added": added, "restored": restored, "existed": existed}

    async def unbind_roles(self, user_id: int, role_ids: Sequence[int]) -> int:
        """为单个用户移除多个角色。

        Args:
            user_id (int): 用户ID。
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            int: 受影响行数。
        """
        async with in_transaction():
            return await self.alive().filter(user_id=user_id, role_id__in=list(role_ids)).update(is_deleted=True)

    async def bind_roles_to_users(self, user_ids: Sequence[int], role_ids: Sequence[int]) -> dict[str, int]:
        """为多个用户批量绑定多个角色。

        Args:
            user_ids (Sequence[int]): 用户ID集合。
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            None: 无返回。
        """
        if not user_ids or not role_ids:
            return {"added": 0, "restored": 0, "existed": 0}
        # 构建目标对
        targets = [(uid, rid) for uid in user_ids for rid in role_ids]
        # 查询现有（包含软删）
        existing = await self.model.filter(user_id__in=list(user_ids), role_id__in=list(role_ids)).all()
        exist_map: dict[tuple[int, int], tuple[int, bool]] = {}
        for x in existing:
            exist_map[(int(x.user.id), int(x.role.id))] = (int(x.id), bool(getattr(x, "is_deleted", False)))
        to_restore_ids: list[int] = []
        to_create_rows: list[dict[str, int]] = []
        for uid, rid in targets:
            hit = exist_map.get((uid, rid))
            if hit is None:
                to_create_rows.append({"user_id": uid, "role_id": rid})
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
                restored += 1  # 占位，稍后以列表长度准
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

    async def unbind_roles_from_users(self, user_ids: Sequence[int], role_ids: Sequence[int]) -> int:
        """为多个用户批量移除多个角色。

        Returns:
            int: 受影响行数。
        """
        async with in_transaction():
            return (
                await self.alive()
                .filter(user_id__in=list(user_ids), role_id__in=list(role_ids))
                .update(is_deleted=True)
            )

    async def list_roles_of_user(self, user_id: int) -> list[UserRole]:
        """查询单个用户的角色关系列表。

        Args:
            user_id (int): 用户ID。

        Returns:
            list[UserRole]: 角色关系列表。
        """
        return await self.alive().filter(user_id=user_id).all()

    async def list_by_user_ids(self, user_ids: Sequence[int]) -> list[UserRole]:
        """按用户ID集合查询角色关系列表。

        Args:
            user_ids (Sequence[int]): 用户ID集合。

        Returns:
            list[UserRole]: 角色关系列表。
        """
        if not user_ids:
            return []
        return await self.alive().filter(user_id__in=list(user_ids)).all()

    async def list_users_of_role(self, role_id: int) -> list[UserRole]:
        """查询角色下的用户关系列表。

        Args:
            role_id (int): 角色ID。

        Returns:
            list[UserRole]: 用户关系列表。
        """
        return await self.alive().filter(role_id=role_id).all()
