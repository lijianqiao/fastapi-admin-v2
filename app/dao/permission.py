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

    async def list_all(
        self, *, include_deleted: bool = True, include_disabled: bool = True, page: int = 1, page_size: int = 20
    ) -> tuple[list[Permission], int]:
        """列出全部权限（未软删），按ID降序。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            tuple[list[Permission], int]: (items, total)。
        """
        q = self.model.all()
        if not include_deleted:
            q = q.filter(is_deleted=False)
        if not include_disabled:
            q = q.filter(is_active=True)
        total = await q.count()
        items = await q.order_by("-id").offset((page - 1) * page_size).limit(page_size)
        return items, total

    async def delete_permission(self, perm_id: int) -> int:
        """软删除权限。

        Args:
            perm_id (int): 权限ID。

        Returns:
            int: 受影响行数。
        """
        return await self.soft_delete(perm_id)

    async def hard_delete_permission(self, perm_id: int) -> int:
        """硬删除权限。

        Args:
            perm_id (int): 权限ID。

        Returns:
            int: 受影响行数。
        """
        return await self.hard_delete(perm_id)

    async def bulk_delete_permissions(self, perm_ids: Sequence[int]) -> int:
        """批量软删除权限。"""
        return await self.bulk_soft_delete(perm_ids)

    async def bulk_hard_delete_permissions(self, perm_ids: Sequence[int]) -> int:
        """批量硬删除权限（谨慎）。"""
        affected = 0
        for pid in perm_ids:
            affected += await self.hard_delete(pid)
        return affected
