"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:40:00
@Docs: 角色服务
"""

from __future__ import annotations

from tortoise.exceptions import IntegrityError

from app.core.constants import Permission as Perm
from app.core.exceptions import conflict, not_found
from app.core.permissions import bump_perm_version
from app.dao.permission import PermissionDAO
from app.dao.role import RoleDAO
from app.dao.role_permission import RolePermissionDAO
from app.schemas.common import BindStats
from app.schemas.permission import PermissionOut
from app.schemas.response import Page
from app.schemas.role import RoleBindIn, RoleCreate, RoleOut, RolesBindIn, RoleUpdate
from app.services.base import BaseService
from app.utils.audit import log_operation


class RoleService(BaseService):
    """角色服务。

    提供角色的创建、更新、查询、分页、禁用，以及权限绑定/解绑（含批量）等能力。
    重要变更会触发权限缓存版本号自增，确保权限及时失效。
    """

    def __init__(
        self,
        role_dao: RoleDAO | None = None,
        role_perm_dao: RolePermissionDAO | None = None,
        perm_dao: PermissionDAO | None = None,
    ) -> None:
        super().__init__(role_dao or RoleDAO())
        self.dao: RoleDAO = role_dao or RoleDAO()
        self.role_perm_dao = role_perm_dao or RolePermissionDAO()
        self.perm_dao = perm_dao or PermissionDAO()

    @log_operation(action=Perm.ROLE_CREATE)
    async def create_role(self, data: RoleCreate, *, actor_id: int | None = None) -> RoleOut:
        """创建角色。

        Args:
            data (RoleCreate): 角色创建入参。
            actor_id (int | None): 操作者ID。

        Returns:
            RoleOut: 新建角色。
        """
        if await self.dao.exists(code=data.code):
            raise conflict("角色编码已存在")
        if await self.dao.exists(name=data.name):
            raise conflict("角色名称已存在")
        try:
            role = await self.dao.create(data.model_dump())
        except IntegrityError as e:
            raise conflict("唯一约束冲突：角色编码/名称已存在") from e
        return RoleOut.model_validate(role)

    @log_operation(action=Perm.ROLE_UPDATE)
    async def update_role(self, role_id: int, version: int, data: RoleUpdate, *, actor_id: int | None = None) -> int:
        """更新角色（乐观锁）。

        Args:
            role_id (int): 角色ID。
            version (int): 当前版本号（乐观锁校验）。
            data (RoleUpdate): 更新入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。

        Raises:
            conflict: 当版本冲突或记录不存在时抛出。
        """
        update_map = dict(data.model_dump(exclude_none=True))
        if not update_map:
            return 0
        try:
            affected = await self.dao.update_with_version(role_id, version, update_map)
        except IntegrityError as e:
            raise conflict("唯一约束冲突：角色编码/名称已存在") from e
        if affected == 0:
            raise conflict("更新冲突或记录不存在")
        return affected

    async def get_role(self, role_id: int) -> RoleOut:
        """查询角色详情。

        Args:
            role_id (int): 角色ID。

        Returns:
            RoleOut: 角色详情。
        """
        role = await self.dao.get_by_id(role_id)
        if not role:
            raise not_found("角色不存在")
        return RoleOut.model_validate(role)

    async def list_roles(self, page: int, page_size: int) -> Page[RoleOut]:
        """分页查询角色。

        Args:
            page (int): 页码，从 1 开始。
            page_size (int): 每页数量。

        Returns:
            Page[RoleOut]: 分页结果。
        """
        items, total = await self.dao.list_paginated(page=page, page_size=page_size, order_by=["name"])
        return Page[RoleOut](
            items=[RoleOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.ROLE_DISABLE)
    async def disable_roles(self, ids: list[int], *, actor_id: int | None = None) -> int:
        """批量禁用角色。

        Args:
            ids (list[int]): 角色ID列表。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        return await self.dao.disable_roles(ids)

    @log_operation(action=Perm.ROLE_DELETE)
    async def delete_role(self, role_id: int, *, hard: bool = False, actor_id: int | None = None) -> int:
        """删除角色（默认软删，hard=True 则硬删）。

        Args:
            role_id (int): 角色ID。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        return await (self.dao.hard_delete_role(role_id) if hard else self.dao.delete_role(role_id))

    @log_operation(action=Perm.ROLE_DELETE)
    async def delete_roles(self, ids: list[int], *, hard: bool = False, actor_id: int | None = None) -> int:
        """批量删除角色（默认软删，hard=True 硬删）。

        Args:
            ids (list[int]): 角色ID列表。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        return await (self.dao.bulk_hard_delete_roles(ids) if hard else self.dao.bulk_delete_roles(ids))

    async def list_all_roles(
        self, *, include_deleted: bool, include_disabled: bool, page: int, page_size: int
    ) -> Page[RoleOut]:
        """列出全部角色（未软删），按ID降序。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            Page[RoleOut]: 分页结果。
        """
        items, total = await self.dao.list_all(
            include_deleted=include_deleted, include_disabled=include_disabled, page=page, page_size=page_size
        )
        return Page[RoleOut](
            items=[RoleOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.ROLE_BIND_PERMISSIONS)
    async def bind_permissions(self, data: RoleBindIn, *, actor_id: int | None = None) -> BindStats:
        """为角色绑定权限。

        Args:
            data (RoleBindIn): 角色与权限绑定入参。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        # 验证角色是否存在
        role = await self.dao.alive().filter(id=data.role_id).first()
        if not role:
            raise not_found("角色不存在")

        # 验证权限是否存在
        if data.target_ids:
            existing_perms = await self.perm_dao.alive().filter(id__in=data.target_ids).values_list("id", flat=True)
            missing_perm_ids = [pid for pid in data.target_ids if pid not in existing_perms]
            if missing_perm_ids:
                raise not_found(f"权限不存在: {missing_perm_ids}")

        stats = await self.role_perm_dao.bind_permissions(data.role_id, data.target_ids)
        await bump_perm_version()
        return BindStats(**stats)

    async def list_permissions(self, role_id: int) -> list[PermissionOut]:
        """列出角色的权限列表。

        Args:
            role_id (int): 角色ID。

        Returns:
            list[PermissionOut]: 权限列表。
        """
        rels = await self.role_perm_dao.list_permissions_of_role(role_id)
        perm_ids = [r.permission_id for r in rels]  # type: ignore[attr-defined]
        perms = []
        if perm_ids:
            perms = await self.perm_dao.get_many_by_ids(perm_ids)
        return [PermissionOut.model_validate(x) for x in perms]

    @log_operation(action=Perm.ROLE_BIND_PERMISSIONS_BATCH)
    async def bind_permissions_batch(self, data: RolesBindIn, *, actor_id: int | None = None) -> BindStats:
        """为多个角色批量绑定多个权限。

        Args:
            data (RolesBindIn): 批量绑定入参。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        stats = await self.role_perm_dao.bind_permissions_to_roles(data.role_ids, data.permission_ids)
        await bump_perm_version()
        return BindStats(**stats)

    @log_operation(action=Perm.ROLE_UNBIND_PERMISSIONS)
    async def unbind_permissions(self, data: RoleBindIn, *, actor_id: int | None = None) -> int:
        """为角色移除权限。

        Args:
            data (RoleBindIn): 解绑入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        affected = await self.role_perm_dao.unbind_permissions_from_roles([data.role_id], data.target_ids)
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.ROLE_UNBIND_PERMISSIONS_BATCH)
    async def unbind_permissions_batch(self, data: RolesBindIn, *, actor_id: int | None = None) -> int:
        """为多个角色批量移除多个权限。

        Args:
            data (RolesBindIn): 批量解绑入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        affected = await self.role_perm_dao.unbind_permissions_from_roles(data.role_ids, data.permission_ids)
        if affected:
            await bump_perm_version()
        return affected
