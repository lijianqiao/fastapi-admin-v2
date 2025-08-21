"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user_role.py
@DateTime: 2025/08/21 11:05:00
@Docs: 用户-角色关系 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from app.dao.base import BaseDAO
from app.models import UserRole


class UserRoleDAO(BaseDAO[UserRole]):
    def __init__(self) -> None:
        super().__init__(UserRole)

    async def bind_roles(self, user_id: int, role_ids: Sequence[int]) -> None:
        rows = [{"user_id": user_id, "role_id": rid} for rid in role_ids]
        await self.bulk_create(rows)

    async def unbind_roles(self, user_id: int, role_ids: Sequence[int]) -> int:
        return await self.alive().filter(user_id=user_id, role_id__in=list(role_ids)).update(is_deleted=True)

    async def bind_roles_to_users(self, user_ids: Sequence[int], role_ids: Sequence[int]) -> None:
        rows = [{"user_id": uid, "role_id": rid} for uid in user_ids for rid in role_ids]
        if rows:
            await self.bulk_create(rows)

    async def unbind_roles_from_users(self, user_ids: Sequence[int], role_ids: Sequence[int]) -> int:
        return await self.alive().filter(user_id__in=list(user_ids), role_id__in=list(role_ids)).update(is_deleted=True)

    async def list_roles_of_user(self, user_id: int) -> list[UserRole]:
        return await self.alive().filter(user_id=user_id).all()

    async def list_by_user_ids(self, user_ids: Sequence[int]) -> list[UserRole]:
        if not user_ids:
            return []
        return await self.alive().filter(user_id__in=list(user_ids)).all()
