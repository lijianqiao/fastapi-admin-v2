"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permissions.py
@DateTime: 2025/08/21 12:10:00
@Docs: 权限检查工具
"""

from collections.abc import Iterable
from typing import Final

from app.dao.permission import PermissionDAO
from app.dao.role import RoleDAO
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
    # super_admin 直通：若用户拥有超级管理员角色，直接放行
    try:
        super_role = await RoleDAO().find_by_code("super_admin")
        if super_role and int(super_role.id) in role_ids:  # type: ignore[arg-type]
            return {"__ALL__"}
    except Exception:
        # 无法判断时忽略直通，走常规权限计算
        pass
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
    empty_key = f"{key}:empty"
    # 优先缓存
    user_perm_set: set[str] | None = None
    # 命中集合缓存
    if await cm.exists(key):
        try:
            user_perm_set = await cm.smembers(key)
            if not user_perm_set:
                return False
        except Exception:
            # 历史版本可能写入为字符串，导致类型冲突：清理并视为未命中
            try:
                await cm.delete(key)
            except Exception:
                pass
            user_perm_set = set()
    # 命中空标记
    elif await cm.exists(empty_key):
        return False
    else:
        # 回源
        user_perm_set = await _load_user_permissions_from_db(user_id)
        if user_perm_set:
            await cm.sadd(key, *list(user_perm_set))
            await cm.expire(key, 1800)
        else:
            # 空权限标记：单独键，避免与集合键类型冲突
            await cm.set(empty_key, "1", ttl=60)
            user_perm_set = set()
    # 检查
    req_set = set(required)
    return req_set.issubset(user_perm_set or set())


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
    empty_key = f"{key}:empty"
    await cm.delete(key, empty_key)


__all__ = ["user_has_permissions", "bump_perm_version", "invalidate_user_permissions"]
