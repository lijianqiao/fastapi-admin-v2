"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: builtin_rbac.py
@DateTime: 2025/08/21 13:20:00
@Docs: 内置角色与权限定义
"""

from typing import TypedDict

from app.core.constants import Permission as Perm


class PermissionDef(TypedDict):
    code: str
    name: str
    description: str


class RoleDef(TypedDict):
    code: str
    name: str
    description: str


def get_builtin_permissions() -> list[PermissionDef]:
    """获取内置权限定义（直接读取枚举的 title/description）。

    Returns:
        list[PermissionDef]: 权限定义列表。
    """
    return [
        {"code": p.value, "name": getattr(p, "title", p.value), "description": getattr(p, "description", p.value)}
        for p in Perm
    ]


def get_builtin_roles() -> list[RoleDef]:
    """获取内置角色定义。

    Returns:
        list[RoleDef]: 角色定义列表。
    """
    return [
        {"code": "super_admin", "name": "超级管理员", "description": "拥有系统全部权限"},
        {"code": "admin", "name": "管理员", "description": "日常管理角色"},
        {"code": "auditor", "name": "审计员", "description": "审计日志查看"},
    ]


def get_role_permission_map() -> dict[str, list[str]]:
    """获取角色到权限编码的映射关系（统一输出字符串 code）。

    Returns:
        dict[str, list[str]]: 角色编码 -> 权限编码列表。
    """
    all_perms: list[Perm] = list(Perm)

    mapping_raw: dict[str, list[Perm]] = {
        "super_admin": all_perms,  # 全量权限
        "admin": [
            Perm.USER_LIST,
            Perm.USER_LIST_ALL,
            Perm.USER_CREATE,
            Perm.USER_UPDATE,
            Perm.USER_DISABLE,
            Perm.USER_BULK_DELETE,
            Perm.USER_HARD_DELETE,
            Perm.USER_UNLOCK,
            Perm.ROLE_LIST,
            Perm.ROLE_LIST_ALL,
            Perm.ROLE_CREATE,
            Perm.ROLE_UPDATE,
            Perm.ROLE_HARD_DELETE,
            Perm.ROLE_BULK_DELETE,
            Perm.PERMISSION_LIST,
            Perm.PERMISSION_LIST_ALL,
            Perm.PERMISSION_CREATE,
            Perm.PERMISSION_UPDATE,
            Perm.PERMISSION_BULK_DELETE,
            Perm.PERMISSION_HARD_DELETE,
            Perm.LOG_LIST,
            Perm.LOG_SELF,
        ],
        "auditor": [Perm.LOG_LIST],
    }

    # 统一转换为 str code
    return {role: [c.value for c in codes] for role, codes in mapping_raw.items()}


__all__ = [
    "PermissionDef",
    "RoleDef",
    "get_builtin_permissions",
    "get_builtin_roles",
    "get_role_permission_map",
]
