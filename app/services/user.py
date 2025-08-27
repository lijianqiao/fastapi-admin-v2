"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:40:00
@Docs: 用户服务
"""

from __future__ import annotations

from tortoise.exceptions import IntegrityError

from app.core.constants import Permission as Perm
from app.core.exceptions import conflict, not_found
from app.core.permissions import bump_perm_version
from app.core.security import hash_password, verify_password
from app.dao.system_config import SystemConfigDAO
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.schemas.common import BindStats
from app.schemas.response import Page
from app.schemas.user import (
    AdminChangePasswordIn,
    SelfChangePasswordIn,
    UserBindIn,
    UserCreate,
    UserOut,
    UserQuery,
    UsersBindIn,
    UserUpdate,
)
from app.services.base import BaseService
from app.utils.audit import log_operation
from app.utils.password_policy import validate_password


class UserService(BaseService):
    """用户服务。

    提供用户的创建、更新、查询、分页、禁用，以及角色绑定/解绑（含批量）等能力。
    重要变更会触发权限缓存版本号自增，确保权限及时失效。
    """

    def __init__(self, user_dao: UserDAO | None = None, user_role_dao: UserRoleDAO | None = None) -> None:
        super().__init__(user_dao or UserDAO())
        self.dao: UserDAO = user_dao or UserDAO()
        self.user_role_dao = user_role_dao or UserRoleDAO()
        self._syscfg = SystemConfigDAO()

    async def _ensure_password_policy(self, password: str) -> None:
        cfg = await self._syscfg.get_singleton()
        ok = validate_password(
            password,
            min_length=cfg.password_min_length or 8,
            require_uppercase=bool(getattr(cfg, "password_require_uppercase", False)),
            require_lowercase=bool(getattr(cfg, "password_require_lowercase", False)),
            require_digits=bool(getattr(cfg, "password_require_digits", False)),
            require_special=bool(getattr(cfg, "password_require_special", False)),
        )
        if not ok:
            raise conflict("密码不符合安全策略")

    @log_operation(action=Perm.USER_CREATE)
    async def create_user(self, data: UserCreate, *, actor_id: int | None = None) -> UserOut:
        """创建用户。

        Args:
            data (UserCreate): 创建用户的入参。
            actor_id (int | None): 操作者用户ID，用于审计日志记录。

        Returns:
            UserOut: 新建用户的出参模型。

        Raises:
            conflict: 当用户名或手机号已存在时抛出。
        """
        # 唯一性预校验
        if await self.dao.exists(username=data.username):
            raise conflict("用户名已存在")
        if await self.dao.exists(phone=data.phone):
            raise conflict("手机号已存在")
        if data.email is not None and data.email != "":
            if await self.dao.exists(email=data.email):
                raise conflict("邮箱已存在")
        # 校验密码策略
        await self._ensure_password_policy(data.password)
        # 构造持久化数据
        to_create = {
            "username": data.username,
            "phone": data.phone,
            "email": data.email,
            "password_hash": hash_password(data.password),
            "nickname": data.nickname,
            "bio": data.bio,
            "avatar_url": data.avatar_url,
        }
        try:
            user = await self.dao.create(to_create)
        except IntegrityError as e:
            # 双保险：数据库唯一约束冲突时返回友好错误
            raise conflict("唯一约束冲突：用户名/手机号/邮箱已存在") from e
        return UserOut.model_validate(user)

    @log_operation(action=Perm.USER_UPDATE)
    async def update_user(self, user_id: int, version: int, data: UserUpdate, *, actor_id: int | None = None) -> int:
        """更新用户（乐观锁）。

        Args:
            user_id (int): 用户ID。
            version (int): 当前版本号（乐观锁校验）。
            data (UserUpdate): 更新入参（部分字段可选）。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数，0 表示无更新或冲突。

        Raises:
            conflict: 当版本冲突或记录不存在时抛出。
        """
        update_map: dict[str, object] = {}
        if data.username is not None:
            update_map["username"] = data.username
        if data.phone is not None:
            update_map["phone"] = data.phone
        if data.email is not None:
            update_map["email"] = data.email
        if data.nickname is not None:
            update_map["nickname"] = data.nickname
        if data.bio is not None:
            update_map["bio"] = data.bio
        if data.avatar_url is not None:
            update_map["avatar_url"] = data.avatar_url
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
        """查询用户详情（附带角色与权限）。

        Args:
            user_id (int): 用户ID。

        Returns:
            UserOut: 用户详情。

        Raises:
            not_found: 当用户不存在时抛出。
        """
        user = await self.dao.get_by_id(user_id)
        if not user:
            raise not_found("用户不存在")
        # 组装角色与权限（按需查询）
        await self.user_role_dao.list_roles_of_user(user_id)
        # 返回基本用户信息，角色/权限可在 API 层扩展字段返回
        return UserOut.model_validate(user)

    async def list_users(self, query: UserQuery, page: int, page_size: int) -> Page[UserOut]:
        """分页查询用户。

        Args:
            query (UserQuery): 查询条件（支持关键词）。
            page (int): 页码，从 1 开始。
            page_size (int): 每页数量。

        Returns:
            Page[UserOut]: 分页结果。
        """
        if query.keyword:
            items, total = await self.dao.search(query.keyword, page=page, page_size=page_size)
        else:
            items, total = await self.dao.list_paginated(page=page, page_size=page_size)
        return Page[UserOut](
            items=[UserOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.USER_DISABLE)
    async def disable_users(self, ids: list[int], *, actor_id: int | None = None) -> int:
        """批量禁用用户。

        Args:
            ids (list[int]): 用户ID列表。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        return await self.dao.disable_users(ids)

    @log_operation(action=Perm.USER_DELETE)
    async def delete_user(self, user_id: int, *, hard: bool = False, actor_id: int | None = None) -> int:
        """删除用户（默认软删，hard=True 则硬删）。

        Args:
            user_id (int): 用户ID。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        affected = await (self.dao.hard_delete_user(user_id) if hard else self.dao.delete_user(user_id))
        return affected

    @log_operation(action=Perm.USER_DELETE)
    async def delete_users(self, ids: list[int], *, hard: bool = False, actor_id: int | None = None) -> int:
        """批量删除用户（默认软删，hard=True 硬删）。

        Args:
            ids (list[int]): 用户ID列表。
            hard (bool): 是否硬删。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            int: 受影响行数。
        """
        return await (self.dao.bulk_hard_delete_users(ids) if hard else self.dao.bulk_delete_users(ids))

    async def list_all_users(
        self, *, include_deleted: bool, include_disabled: bool, page: int, page_size: int
    ) -> Page[UserOut]:
        """列出全部用户（未软删），按ID降序。

        Args:
            include_deleted (bool): 是否包含软删。
            include_disabled (bool): 是否包含禁用。
            page (int): 页码。
            page_size (int): 每页数量。

        Returns:
            Page[UserOut]: 分页结果。
        """
        items, total = await self.dao.list_all(
            include_deleted=include_deleted, include_disabled=include_disabled, page=page, page_size=page_size
        )
        return Page[UserOut](
            items=[UserOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size
        )

    @log_operation(action=Perm.USER_BIND_ROLES)
    async def bind_roles(self, data: UserBindIn, *, actor_id: int | None = None) -> None:
        """为用户绑定角色。

        Args:
            data (UserBindIn): 用户与角色绑定入参。
            actor_id (int | None): 操作者ID，用于审计日志记录。

        Returns:
            None: 无返回。
        """
        await self.user_role_dao.bind_roles(data.user_id, data.role_ids)
        await bump_perm_version()

    @log_operation(action=Perm.USER_BIND_ROLES_BATCH)
    async def bind_roles_batch(self, data: UsersBindIn, *, actor_id: int | None = None) -> BindStats:
        """为多个用户批量绑定多个角色。

        Args:
            data (UsersBindIn): 批量绑定入参。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        # 验证用户是否存在
        if data.user_ids:
            existing_users = await self.dao.alive().filter(id__in=data.user_ids).values_list("id", flat=True)
            missing_user_ids = [uid for uid in data.user_ids if uid not in existing_users]
            if missing_user_ids:
                raise not_found(f"用户不存在: {missing_user_ids}")

        # 验证角色是否存在
        if data.role_ids:
            from app.dao.role import RoleDAO

            role_dao = RoleDAO()
            existing_roles = await role_dao.alive().filter(id__in=data.role_ids).values_list("id", flat=True)
            missing_role_ids = [rid for rid in data.role_ids if rid not in existing_roles]
            if missing_role_ids:
                raise not_found(f"角色不存在: {missing_role_ids}")

        stats = await self.user_role_dao.bind_roles_to_users(data.user_ids, data.role_ids)
        await bump_perm_version()
        return BindStats(**stats)

    @log_operation(action=Perm.USER_UNBIND_ROLES)
    async def unbind_roles(self, data: UserBindIn, *, actor_id: int | None = None) -> int:
        """为用户移除角色。

        Args:
            data (UserBindIn): 用户与角色解绑入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        affected = await self.user_role_dao.unbind_roles(data.user_id, data.role_ids)
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.USER_UNBIND_ROLES_BATCH)
    async def unbind_roles_batch(self, data: UsersBindIn, *, actor_id: int | None = None) -> int:
        """为多个用户批量移除多个角色。

        Args:
            data (UsersBindIn): 批量解绑入参。
            actor_id (int | None): 操作者ID。

        Returns:
            int: 受影响行数。
        """
        affected = await self.user_role_dao.unbind_roles_from_users(data.user_ids, data.role_ids)
        if affected:
            await bump_perm_version()
        return affected

    @log_operation(action=Perm.USER_UPDATE)
    async def admin_change_password(
        self, user_id: int, payload: AdminChangePasswordIn, *, actor_id: int | None = None
    ) -> None:
        """管理员修改指定用户密码（无需旧密码）。

        Args:
            user_id (int): 用户ID。
            payload (AdminChangePasswordIn): 修改密码入参。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        if payload.new_password != payload.confirm_password:
            raise conflict("两次密码不一致")
        user = await self.dao.get_by_id(user_id)
        if not user:
            raise not_found("用户不存在")
        await self._ensure_password_policy(payload.new_password)
        hashed = hash_password(payload.new_password)
        affected = await self.dao.update_with_version(user.id, version=user.version, data={"password_hash": hashed})
        if affected == 0:
            raise conflict("更新冲突或记录不存在")

    @log_operation(action=Perm.USER_UPDATE)
    async def self_change_password(
        self, user_id: int, payload: SelfChangePasswordIn, *, actor_id: int | None = None
    ) -> None:
        """用户自助修改密码（需要旧密码验证）。

        Args:
            user_id (int): 用户ID。
            payload (SelfChangePasswordIn): 修改密码入参。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        user = await self.dao.get_by_id(user_id)
        if not user:
            raise not_found("用户不存在")
        if not verify_password(payload.old_password, user.password_hash):
            raise conflict("旧密码不正确")
        if payload.new_password != payload.confirm_password:
            raise conflict("两次密码不一致")
        await self._ensure_password_policy(payload.new_password)
        hashed = hash_password(payload.new_password)
        await self.dao.update_with_version(user.id, version=user.version, data={"password_hash": hashed})

    @log_operation(action=Perm.USER_UNLOCK)
    async def unlock_user(self, user_id: int, *, actor_id: int | None = None) -> None:
        """解锁用户（清除锁定与失败计数）。

        Args:
            user_id (int): 用户ID。
            actor_id (int | None): 操作者ID。

        Returns:
            None: 无返回。
        """
        user = await self.dao.get_by_id(user_id)
        if not user:
            raise not_found("用户不存在")
        await self.dao.update_with_version(
            user.id, version=user.version, data={"failed_attempts": 0, "locked_until": None}
        )
