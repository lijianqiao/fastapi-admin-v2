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

    async def list_all(self) -> list[Role]:
        """列出全部角色（未软删），按名称升序。

        Returns:
            list[Role]: 角色列表。
        """
        return await self.alive().order_by("name").all()
