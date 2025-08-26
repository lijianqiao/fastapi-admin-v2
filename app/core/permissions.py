"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permissions.py
@DateTime: 2025/08/21 12:10:00
@Docs: 权限检查工具
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Final

from app.dao.permission import PermissionDAO
from app.dao.role_permission import RolePermissionDAO
from app.dao.user_role import UserRoleDAO
from app.utils.cache_manager import CacheManager, get_cache_manager

PERM_VERSION_KEY: Final[str] = "rbac:perm:version"


def _cache_key(user_id: int, version: int) -> str:
    """缓存键

    Args:
        user_id (int): 用户ID
        version (int): 版本号

    Returns:
        str: 缓存键
    """
    return f"rbac:perm:v{version}:u:{user_id}"


async def _get_perm_version(cm: CacheManager) -> int:
    """获取权限版本

    Args:
        cm (CacheManager): 缓存管理器

    Returns:
        int: 权限版本
    """
    return await cm.get_version(PERM_VERSION_KEY, default=1)


async def bump_perm_version() -> int:
    """提升权限版本

    Returns:
        int: 提升后的权限版本
    """
    cm = get_cache_manager()
    return await cm.bump_version(PERM_VERSION_KEY)


async def _load_user_permissions_from_db(user_id: int) -> set[str]:
    """从数据库加载用户权限

    Args:
        user_id (int): 用户ID

    Returns:
        set[str]: 用户权限集合
    """
    # 获取用户角色
    user_role_dao = UserRoleDAO()
    role_perm_dao = RolePermissionDAO()
    perm_dao = PermissionDAO()
    user_roles = await user_role_dao.list_roles_of_user(user_id)
    role_ids = [ur.role_id for ur in user_roles]  # type: ignore[attr-defined]
    if not role_ids:
        return set()
    # 角色-权限关系
    rels = await role_perm_dao.list_by_role_ids(role_ids)
    perm_ids = [rp.permission_id for rp in rels]  # type: ignore[attr-defined]
    if not perm_ids:
        return set()
    # 权限code集合
    perms = await perm_dao.list_by_ids(perm_ids)
    return {p.code for p in perms}


async def user_has_permissions(user_id: int, required: Iterable[str]) -> bool:
    """检查用户是否有权限

    Args:
        user_id (int): 用户ID
        required (Iterable[str]): 需要的权限

    Returns:
        bool: 是否有权限
    """
    cm = get_cache_manager()
    version = await _get_perm_version(cm)
    key = _cache_key(user_id, version)
    # 优先缓存
    if await cm.exists(key):
        user_perm_set = await cm.smembers(key)
        # 空权限标记：当集合为空且存在同名字符串键（短TTL），直接视为无权限
        if not user_perm_set:
            return False
    else:
        # 回源
        user_perm_set = await _load_user_permissions_from_db(user_id)
        if user_perm_set:
            await cm.sadd(key, *list(user_perm_set))
            await cm.expire(key, 1800)
        else:
            # 空权限标记：写一个短TTL字符串键，避免频繁回源
            await cm.set(key, "__empty__", ttl=60)
    # 检查
    req_set = set(required)
    return req_set.issubset(user_perm_set)


async def invalidate_user_permissions(user_id: int) -> None:
    """失效指定用户的当前版本权限集合缓存。

    Args:
        user_id (int): 用户ID。

    Returns:
        None: 无返回。
    """
    cm = get_cache_manager()
    version = await _get_perm_version(cm)
    key = _cache_key(user_id, version)
    await cm.delete(key)


__all__ = ["user_has_permissions", "bump_perm_version", "invalidate_user_permissions"]
