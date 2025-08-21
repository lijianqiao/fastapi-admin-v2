"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:05:00
@Docs: 角色 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from app.dao.base import BaseDAO
from app.models import Role


class RoleDAO(BaseDAO[Role]):
    def __init__(self) -> None:
        super().__init__(Role)

    async def find_by_code(self, code: str) -> Role | None:
        return await self.alive().filter(code=code).first()

    async def disable_roles(self, role_ids: Sequence[int]) -> int:
        return await self.alive().filter(id__in=list(role_ids)).update(is_active=False)

    async def list_all(self) -> list[Role]:
        return await self.alive().order_by("name").all()
