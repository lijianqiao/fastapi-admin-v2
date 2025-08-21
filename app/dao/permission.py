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
    """权限数据访问对象。

    提供权限编码查询、批量禁用与集合查询等能力。
    """

    def __init__(self) -> None:
        super().__init__(Permission)

    async def find_by_code(self, code: str) -> Permission | None:
        """按权限编码查询（未软删）。

        Args:
            code (str): 权限编码。

        Returns:
            Permission | None: 权限或 None。
        """
        return await self.alive().filter(code=code).first()

    async def disable_permissions(self, perm_ids: Sequence[int]) -> int:
        """批量禁用权限。

        Args:
            perm_ids (Sequence[int]): 权限ID集合。

        Returns:
            int: 受影响行数。
        """
        return await self.alive().filter(id__in=list(perm_ids)).update(is_active=False)

    async def list_by_ids(self, ids: Sequence[int]) -> list[Permission]:
        """按 ID 集合查询权限列表（未软删）。

        Args:
            ids (Sequence[int]): 权限ID集合。

        Returns:
            list[Permission]: 权限列表。
        """
        if not ids:
            return []
        return await self.alive().filter(id__in=list(ids)).all()

    async def list_by_codes(self, codes: Sequence[str]) -> list[Permission]:
        """按编码集合查询权限列表（未软删）。

        Args:
            codes (Sequence[str]): 权限编码集合。

        Returns:
            list[Permission]: 权限列表。
        """
        return await self.alive().filter(code__in=list(codes)).all()
