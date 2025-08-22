"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permission.py
@DateTime: 2025/08/21 11:40:00
@Docs: 权限服务
"""

from __future__ import annotations

from tortoise.exceptions import IntegrityError

from app.core.constants import Permission as Perm
from app.core.exceptions import conflict, not_found
from app.core.permissions import bump_perm_version
from app.dao.permission import PermissionDAO
from app.schemas.permission import PermissionCreate, PermissionOut, PermissionUpdate
from app.schemas.response import Page
from app.services.base import BaseService
from app.utils.audit import log_operation


class PermissionService(BaseService):
    """权限服务。

    提供权限的创建、更新、查询、分页、禁用等能力。重要变更会触发权限缓存版本号自增。
    """

    def __init__(self, perm_dao: PermissionDAO | None = None) -> None:
        super().__init__(perm_dao or PermissionDAO())

    @log_operation(action=Perm.PERMISSION_CREATE)
    async def create_permission(self, data: PermissionCreate, *, actor_id: int | None = None) -> PermissionOut:
        """创建权限。

        Args:
            data (PermissionCreate): 权限创建入参。
            actor_id (int | None): 操作者ID。

        Returns:
            PermissionOut: 新建权限。
        """
        if await self.dao.exists(code=data.code):
            raise conflict("权限编码已存在")
        if await self.dao.exists(name=data.name):
            raise conflict("权限名称已存在")
        try:
            perm = await self.dao.create(data.model_dump())
        except IntegrityError as e:
            raise conflict("唯一约束冲突：权限编码/名称已存在") from e
        await bump_perm_version()
        return PermissionOut.model_validate(perm)

    @log_operation(action=Perm.PERMISSION_UPDATE)
    async def update_permission(
        self, perm_id: int, version: int, data: PermissionUpdate, *, actor_id: int | None = None
    ) -> int:
        """更新权限（乐观锁）。

        Args:
            perm_id (int): 权限ID。
            version (int): 当前版本号（乐观锁校验）。
            data (PermissionUpdate): 更新入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        update_map = dict(data.model_dump(exclude_none=True).items())
        if not update_map:
            return 0
        try:
            affected = await self.dao.update_with_version(perm_id, version, update_map)
        except IntegrityError as e:
            raise conflict("唯一约束冲突：权限编码/名称已存在") from e
        if affected == 0:
            raise conflict("更新冲突或记录不存在")
        await bump_perm_version()
        return affected

    async def get_permission(self, perm_id: int) -> PermissionOut:
        """查询权限详情。

        Args:
            perm_id (int): 权限ID。

        Returns:
            PermissionOut: 权限详情。
        """
        perm = await self.dao.get_by_id(perm_id)
        if not perm:
            raise not_found("权限不存在")
        return PermissionOut.model_validate(perm)

    async def list_permissions(self, page: int, page_size: int) -> Page[PermissionOut]:
        """分页查询权限。

        Args:
            page (int): 页码，从 1 开始。
            page_size (int): 每页数量。

        Returns:
            Page[PermissionOut]: 分页结果。
        """
        items, total = await self.dao.list_paginated(page=page, page_size=page_size, order_by=["code"])
        return Page[PermissionOut](
            items=[PermissionOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.PERMISSION_DISABLE)
    async def disable_permissions(self, ids: list[int], *, actor_id: int | None = None) -> int:
        """批量禁用权限。

        Args:
            ids (list[int]): 权限ID列表。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        affected = await PermissionDAO().disable_permissions(ids)
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.PERMISSION_DELETE)
    async def delete_permission(self, perm_id: int, *, hard: bool = False, actor_id: int | None = None) -> int:
        """删除权限（默认软删，hard=True 则硬删）。

        Args:
            perm_id (int): 权限ID。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        affected = await (self.dao.hard_delete_permission(perm_id) if hard else self.dao.delete_permission(perm_id))
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.PERMISSION_DELETE)
    async def delete_permissions(self, ids: list[int], *, hard: bool = False, actor_id: int | None = None) -> int:
        """批量删除权限（默认软删，hard=True 硬删）。

        Args:
            ids (list[int]): 权限ID列表。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        affected = await (self.dao.bulk_hard_delete_permissions(ids) if hard else self.dao.bulk_delete_permissions(ids))
        if affected:
            await bump_perm_version()
        return affected

    async def list_all_permissions(
        self, *, include_deleted: bool, include_disabled: bool, page: int, page_size: int
    ) -> Page[PermissionOut]:
        """列出全部权限（未软删），按ID降序。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            Page[PermissionOut]: 分页结果。
        """
        items, total = await self.dao.list_all(
            include_deleted=include_deleted, include_disabled=include_disabled, page=page, page_size=page_size
        )
        return Page[PermissionOut](
            items=[PermissionOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )
