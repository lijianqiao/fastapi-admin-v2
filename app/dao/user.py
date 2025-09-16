"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:05:00
@Docs: 用户 DAO
"""

from collections.abc import Sequence

from tortoise.expressions import Q

from app.dao.base import BaseDAO
from app.models import User


class UserDAO(BaseDAO[User]):
    """用户数据访问对象。

    提供用户维度的常见查询与批量操作封装。
    """

    def __init__(self) -> None:
        super().__init__(User)

    async def find_by_username(self, username: str) -> User | None:
        """按用户名查询用户（未软删）。

        Args:
            username (str): 用户名。

        Returns:
            User | None: 用户实体或 None。
        """
        return await self.alive().filter(username=username).first()

    async def find_by_phone(self, phone: str) -> User | None:
        """按手机号查询用户（未软删）。

        Args:
            phone (str): 手机号。

        Returns:
            User | None: 用户实体或 None。
        """
        return await self.alive().filter(phone=phone).first()

    async def disable_users(self, user_ids: Sequence[int]) -> int:
        """批量禁用用户。

        Args:
            user_ids (Sequence[int]): 用户ID集合。

        Returns:
            int: 受影响行数。
        """
        return await self.alive().filter(id__in=list(user_ids)).update(is_active=False)

    async def search(self, keyword: str, *, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        """按用户名/手机号模糊搜索并分页。

        Args:
            keyword (str): 关键字。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            tuple[list[User], int]: (items, total)。
        """
        q = self.alive().filter(Q(username__icontains=keyword) | Q(phone__icontains=keyword))
        total = await q.count()
        items = await q.order_by("-id").offset((page - 1) * page_size).limit(page_size)
        return items, total

    async def list_all(
        self, *, include_deleted: bool = True, include_disabled: bool = True, page: int = 1, page_size: int = 20
    ) -> tuple[list[User], int]:
        """全量列表（可包含软删/禁用）。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            tuple[list[User], int]: (items, total)。
        """
        q = self.model.all()
        if not include_deleted:
            q = q.filter(is_deleted=False)
        if not include_disabled:
            q = q.filter(is_active=True)
        total = await q.count()
        items = await q.order_by("-id").offset((page - 1) * page_size).limit(page_size)
        return items, total

    async def delete_user(self, user_id: int) -> int:
        """软删除用户。

        Args:
            user_id (int): 用户ID。

        Returns:
            int: 受影响行数。
        """
        return await self.soft_delete(user_id)

    async def hard_delete_user(self, user_id: int) -> int:
        """硬删除用户。

        Args:
            user_id (int): 用户ID。

        Returns:
            int: 受影响行数。
        """
        return await self.hard_delete(user_id)

    async def bulk_delete_users(self, user_ids: Sequence[int]) -> int:
        """批量软删除用户。

        Args:
            user_ids (Sequence[int]): 用户ID集合。

        Returns:
            int: 受影响行数。
        """
        return await self.bulk_soft_delete(user_ids)

    async def bulk_hard_delete_users(self, user_ids: Sequence[int]) -> int:
        """批量硬删除用户（谨慎）。

        Args:
            user_ids (Sequence[int]): 用户ID集合。

        Returns:
            int: 受影响行数。
        """
        affected = 0
        for uid in user_ids:
            affected += await self.hard_delete(uid)
        return affected
