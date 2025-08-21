"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permission.py
@DateTime: 2025/08/21 11:05:00
@Docs: 权限 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from app.dao.base import BaseDAO
from app.models import Permission


class PermissionDAO(BaseDAO[Permission]):
    def __init__(self) -> None:
        super().__init__(Permission)

    async def find_by_code(self, code: str) -> Permission | None:
        return await self.alive().filter(code=code).first()

    async def disable_permissions(self, perm_ids: Sequence[int]) -> int:
        return await self.alive().filter(id__in=list(perm_ids)).update(is_active=False)

    async def list_by_codes(self, codes: Sequence[str]) -> list[Permission]:
        return await self.alive().filter(code__in=list(codes)).all()
