"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:40:00
@Docs: 用户服务
"""

from __future__ import annotations

from app.core.exceptions import conflict, not_found
from app.core.security import hash_password
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.schemas.response import Page
from app.schemas.user import UserBindIn, UserCreate, UserOut, UserQuery, UsersBindIn, UserUpdate
from app.services.base import BaseService


class UserService(BaseService):
    def __init__(self, user_dao: UserDAO | None = None, user_role_dao: UserRoleDAO | None = None) -> None:
        super().__init__(user_dao or UserDAO())
        self.user_role_dao = user_role_dao or UserRoleDAO()

    async def create_user(self, data: UserCreate) -> UserOut:
        # 唯一性预校验
        if await self.dao.exists(username=data.username):
            raise conflict("用户名已存在")
        if await self.dao.exists(phone=data.phone):
            raise conflict("手机号已存在")
        # 构造持久化数据
        to_create = {
            "username": data.username,
            "phone": data.phone,
            "email": data.email,
            "password_hash": hash_password(data.password),
        }
        user = await self.dao.create(to_create)
        return UserOut.model_validate(user)

    async def update_user(self, user_id: int, version: int, data: UserUpdate) -> int:
        update_map: dict[str, object] = {}
        if data.username is not None:
            update_map["username"] = data.username
        if data.phone is not None:
            update_map["phone"] = data.phone
        if data.email is not None:
            update_map["email"] = data.email
        if data.password is not None:
            update_map["password_hash"] = hash_password(data.password)
        if data.is_active is not None:
            update_map["is_active"] = data.is_active
        if not update_map:
            return 0
        affected = await self.dao.update_with_version(user_id, version, update_map)
        if affected == 0:
            raise conflict("更新冲突或记录不存在")
        return affected

    async def get_user(self, user_id: int) -> UserOut:
        user = await self.dao.get_by_id(user_id)
        if not user:
            raise not_found("用户不存在")
        return UserOut.model_validate(user)

    async def list_users(self, query: UserQuery, page: int, page_size: int) -> Page[UserOut]:
        if query.keyword:
            items, total = await self.dao.search(query.keyword, page=page, page_size=page_size)
        else:
            items, total = await self.dao.list_paginated(page=page, page_size=page_size)
        return Page[UserOut](
            items=[UserOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    async def disable_users(self, ids: list[int]) -> int:
        return await self.dao.disable_users(ids)

    async def bind_roles(self, data: UserBindIn) -> None:
        await self.user_role_dao.bind_roles(data.user_id, data.role_ids)

    async def bind_roles_batch(self, data: UsersBindIn) -> None:
        await self.user_role_dao.bind_roles_to_users(data.user_ids, data.role_ids)

    async def unbind_roles(self, data: UserBindIn) -> int:
        return await self.user_role_dao.unbind_roles(data.user_id, data.role_ids)

    async def unbind_roles_batch(self, data: UsersBindIn) -> int:
        return await self.user_role_dao.unbind_roles_from_users(data.user_ids, data.role_ids)
