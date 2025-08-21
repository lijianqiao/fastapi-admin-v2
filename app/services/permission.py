"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permission.py
@DateTime: 2025/08/21 11:40:00
@Docs: 权限服务
"""

from __future__ import annotations

from app.core.exceptions import conflict, not_found
from app.dao.permission import PermissionDAO
from app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate
from app.schemas.response import Page
from app.services.base import BaseService


class PermissionService(BaseService):
    def __init__(self, perm_dao: PermissionDAO | None = None) -> None:
        super().__init__(perm_dao or PermissionDAO())

    async def create_permission(self, data: PermissionCreate) -> PermissionOut:
        if await self.dao.exists(code=data.code):
            raise conflict("权限编码已存在")
        perm = await self.dao.create(data.model_dump())
        return PermissionOut.model_validate(perm)

    async def update_permission(self, perm_id: int, version: int, data: PermissionUpdate) -> int:
        update_map = {k: v for k, v in data.model_dump(exclude_none=True).items()}
        if not update_map:
            return 0
        affected = await self.dao.update_with_version(perm_id, version, update_map)
        if affected == 0:
            raise conflict("更新冲突或记录不存在")
        return affected

    async def get_permission(self, perm_id: int) -> PermissionOut:
        perm = await self.dao.get_by_id(perm_id)
        if not perm:
            raise not_found("权限不存在")
        return PermissionOut.model_validate(perm)

    async def list_permissions(self, page: int, page_size: int) -> Page[PermissionOut]:
        items, total = await self.dao.list_paginated(page=page, page_size=page_size, order_by=["code"])
        return Page[PermissionOut](
            items=[PermissionOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )
