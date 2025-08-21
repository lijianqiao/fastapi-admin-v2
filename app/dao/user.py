"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:05:00
@Docs: 用户 DAO
"""

from __future__ import annotations

from collections.abc import Sequence

from app.dao.base import BaseDAO
from app.models import User


class UserDAO(BaseDAO[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def find_by_username(self, username: str) -> User | None:
        return await self.alive().filter(username=username).first()

    async def find_by_phone(self, phone: str) -> User | None:
        return await self.alive().filter(phone=phone).first()

    async def disable_users(self, user_ids: Sequence[int]) -> int:
        return await self.alive().filter(id__in=list(user_ids)).update(is_active=False)

    async def search(self, keyword: str, *, page: int = 1, page_size: int = 20) -> tuple[list[User], int]:
        q = self.alive().filter(username__icontains=keyword) | self.alive().filter(phone__icontains=keyword)
        total = await q.count()
        items = await q.order_by("-id").offset((page - 1) * page_size).limit(page_size)
        return items, total
