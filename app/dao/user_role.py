"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_role.py
@DateTime: 2025/08/21 11:05:00
@Docs: 用户-角色关系 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from tortoise.transactions import in_transaction

from app.dao.base import BaseDAO
from app.models import UserRole


class UserRoleDAO(BaseDAO[UserRole]):
    """用户-角色关系数据访问对象。"""

    def __init__(self) -> None:
        super().__init__(UserRole)

    async def bind_roles(self, user_id: int, role_ids: Sequence[int]) -> None:
        """为单个用户绑定多个角色。

        Args:
            user_id (int): 用户ID。
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            None: 无返回。
        """
        rows = [{"user_id": user_id, "role_id": rid} for rid in role_ids]
        async with in_transaction():
            await self.bulk_create(rows)

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

    async def bind_roles_to_users(self, user_ids: Sequence[int], role_ids: Sequence[int]) -> None:
        """为多个用户批量绑定多个角色。

        Args:
            user_ids (Sequence[int]): 用户ID集合。
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            None: 无返回。
        """
        rows = [{"user_id": uid, "role_id": rid} for uid in user_ids for rid in role_ids]
        if rows:
            async with in_transaction():
                await self.bulk_create(rows)

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
