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
    """角色数据访问对象。

    提供角色查询、批量停用与有序列表等能力。
    """

    def __init__(self) -> None:
        super().__init__(Role)

    async def list_all(
        self, *, include_deleted: bool = True, include_disabled: bool = True, page: int = 1, page_size: int = 20
    ) -> tuple[list[Role], int]:
        """列出全部角色（未软删），按名称升序。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            tuple[list[Role], int]: (items, total)。
        """
        q = self.model.all()
        if not include_deleted:
            q = q.filter(is_deleted=False)
        if not include_disabled:
            q = q.filter(is_active=True)
        total = await q.count()
        items = await q.order_by("-id").offset((page - 1) * page_size).limit(page_size)
        return items, total

    async def delete_role(self, role_id: int) -> int:
        """软删除角色。

        Args:
            role_id (int): 角色ID。

        Returns:
            int: 受影响行数。
        """
        return await self.soft_delete(role_id)

    async def hard_delete_role(self, role_id: int) -> int:
        """硬删除角色。

        Args:
            role_id (int): 角色ID。

        Returns:
            int: 受影响行数。
        """
        return await self.hard_delete(role_id)

    async def find_by_code(self, code: str) -> Role | None:
        """按角色编码查询角色（未软删）。

        Args:
            code (str): 角色编码。

        Returns:
            Role | None: 角色或 None。
        """
        return await self.alive().filter(code=code).first()

    async def disable_roles(self, role_ids: Sequence[int]) -> int:
        """批量禁用角色。

        Args:
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            int: 受影响行数。
        """
        return await self.alive().filter(id__in=list(role_ids)).update(is_active=False)

    async def bulk_delete_roles(self, role_ids: Sequence[int]) -> int:
        """批量软删除角色。

        Args:
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            int: 受影响行数。
        """
        return await self.bulk_soft_delete(role_ids)

    async def bulk_hard_delete_roles(self, role_ids: Sequence[int]) -> int:
        """批量硬删除角色（谨慎）。

        Args:
            role_ids (Sequence[int]): 角色ID集合。

        Returns:
            int: 受影响行数。
        """
        affected = 0
        for rid in role_ids:
            affected += await self.hard_delete(rid)
        return affected
