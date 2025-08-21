"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:40:00
@Docs: 角色服务
"""

from __future__ import annotations

from app.core.constants import Permission as Perm
from app.core.exceptions import conflict, not_found
from app.core.permissions import bump_perm_version
from app.dao.permission import PermissionDAO
from app.dao.role import RoleDAO
from app.dao.role_permission import RolePermissionDAO
from app.schemas.permission import PermissionOut
from app.schemas.response import Page
from app.schemas.role import RoleBindIn, RoleCreate, RoleOut, RolesBindIn, RoleUpdate
from app.services.base import BaseService
from app.utils.audit import log_operation


class RoleService(BaseService):
    def __init__(
        self,
        role_dao: RoleDAO | None = None,
        role_perm_dao: RolePermissionDAO | None = None,
        perm_dao: PermissionDAO | None = None,
    ) -> None:
        super().__init__(role_dao or RoleDAO())
        self.role_perm_dao = role_perm_dao or RolePermissionDAO()
        self.perm_dao = perm_dao or PermissionDAO()

    @log_operation(action=Perm.ROLE_CREATE)
    async def create_role(self, data: RoleCreate, *, actor_id: int | None = None) -> RoleOut:
        if await self.dao.exists(code=data.code):
            raise conflict("角色编码已存在")
        role = await self.dao.create(data.model_dump())
        return RoleOut.model_validate(role)

    @log_operation(action=Perm.ROLE_UPDATE)
    async def update_role(self, role_id: int, version: int, data: RoleUpdate, *, actor_id: int | None = None) -> int:
        update_map = dict(data.model_dump(exclude_none=True))
        if not update_map:
            return 0
        affected = await self.dao.update_with_version(role_id, version, update_map)
        if affected == 0:
            raise conflict("更新冲突或记录不存在")
        return affected

    async def get_role(self, role_id: int) -> RoleOut:
        role = await self.dao.get_by_id(role_id)
        if not role:
            raise not_found("角色不存在")
        return RoleOut.model_validate(role)

    async def list_roles(self, page: int, page_size: int) -> Page[RoleOut]:
        items, total = await self.dao.list_paginated(page=page, page_size=page_size, order_by=["name"])
        return Page[RoleOut](
            items=[RoleOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.ROLE_DISABLE)
    async def disable_roles(self, ids: list[int], *, actor_id: int | None = None) -> int:
        return await self.dao.disable_roles(ids)

    @log_operation(action=Perm.ROLE_BIND_PERMISSIONS)
    async def bind_permissions(self, data: RoleBindIn, *, actor_id: int | None = None) -> None:
        await self.role_perm_dao.bind_permissions(data.role_id, data.target_ids)
        await bump_perm_version()

    async def list_permissions(self, role_id: int) -> list[PermissionOut]:
        rels = await self.role_perm_dao.list_permissions_of_role(role_id)
        perm_ids = [r.permission_id for r in rels]
        perms = []
        if perm_ids:
            perms = await self.perm_dao.get_many_by_ids(perm_ids)
        return [PermissionOut.model_validate(x) for x in perms]

    @log_operation(action=Perm.ROLE_BIND_PERMISSIONS_BATCH)
    async def bind_permissions_batch(self, data: RolesBindIn, *, actor_id: int | None = None) -> None:
        await self.role_perm_dao.bind_permissions_to_roles(data.role_ids, data.permission_ids)
        await bump_perm_version()

    @log_operation(action=Perm.ROLE_UNBIND_PERMISSIONS)
    async def unbind_permissions(self, data: RoleBindIn, *, actor_id: int | None = None) -> int:
        affected = await self.role_perm_dao.unbind_permissions_from_roles([data.role_id], data.target_ids)
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.ROLE_UNBIND_PERMISSIONS_BATCH)
    async def unbind_permissions_batch(self, data: RolesBindIn, *, actor_id: int | None = None) -> int:
        affected = await self.role_perm_dao.unbind_permissions_from_roles(data.role_ids, data.permission_ids)
        if affected:
            await bump_perm_version()
        return affected
