"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: builtin_rbac.py
@DateTime: 2025/08/21 13:20:00
@Docs: 内置角色与权限定义
"""

from __future__ import annotations

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
    """获取内置权限定义。

    Returns:
        list[PermissionDef]: 权限定义列表。
    """
    return [
        {"code": Perm.USER_LIST, "name": "用户列表", "description": "查看用户列表"},
        {"code": Perm.USER_CREATE, "name": "创建用户", "description": "创建新用户"},
        {"code": Perm.USER_UPDATE, "name": "更新用户", "description": "更新用户信息"},
        {"code": Perm.USER_DELETE, "name": "删除用户", "description": "删除用户"},
        {"code": Perm.USER_BULK_DELETE, "name": "批量删除用户", "description": "批量删除用户"},
        {"code": Perm.USER_DISABLE, "name": "禁用用户", "description": "禁用用户账号"},
        {"code": Perm.USER_HARD_DELETE, "name": "硬删除用户", "description": "不可恢复删除用户"},
        {"code": Perm.USER_LIST_ALL, "name": "用户全量列表", "description": "查看所有用户（含禁用/软删）"},
        {"code": Perm.USER_BIND_ROLES, "name": "用户绑定角色", "description": "为用户绑定角色"},
        {"code": Perm.USER_UNBIND_ROLES, "name": "用户解绑角色", "description": "为用户移除角色"},
        {"code": Perm.USER_BIND_ROLES_BATCH, "name": "批量绑定角色", "description": "批量为用户绑定角色"},
        {"code": Perm.USER_UNBIND_ROLES_BATCH, "name": "批量解绑角色", "description": "批量为用户移除角色"},
        {"code": Perm.USER_UNLOCK, "name": "解锁用户", "description": "解除用户登录锁定"},
        {"code": Perm.ROLE_LIST, "name": "角色列表", "description": "查看角色列表"},
        {"code": Perm.ROLE_CREATE, "name": "创建角色", "description": "创建新角色"},
        {"code": Perm.ROLE_UPDATE, "name": "更新角色", "description": "更新角色信息"},
        {"code": Perm.ROLE_DELETE, "name": "删除角色", "description": "删除角色"},
        {"code": Perm.ROLE_BULK_DELETE, "name": "批量删除角色", "description": "批量删除角色"},
        {"code": Perm.ROLE_DISABLE, "name": "禁用角色", "description": "禁用角色"},
        {"code": Perm.ROLE_HARD_DELETE, "name": "硬删除角色", "description": "不可恢复删除角色"},
        {"code": Perm.ROLE_LIST_ALL, "name": "角色全量列表", "description": "查看所有角色（含禁用/软删）"},
        {"code": Perm.ROLE_BIND_PERMISSIONS, "name": "绑定权限", "description": "为角色绑定权限"},
        {"code": Perm.ROLE_UNBIND_PERMISSIONS, "name": "解绑权限", "description": "为角色解绑权限"},
        {"code": Perm.ROLE_BIND_PERMISSIONS_BATCH, "name": "批量绑定权限", "description": "批量为角色绑定权限"},
        {"code": Perm.ROLE_UNBIND_PERMISSIONS_BATCH, "name": "批量解绑权限", "description": "批量为角色解绑权限"},
        {"code": Perm.PERMISSION_LIST, "name": "权限列表", "description": "查看权限列表"},
        {"code": Perm.PERMISSION_CREATE, "name": "创建权限", "description": "创建权限项"},
        {"code": Perm.PERMISSION_UPDATE, "name": "更新权限", "description": "更新权限项"},
        {"code": Perm.PERMISSION_DELETE, "name": "删除权限", "description": "删除权限项"},
        {"code": Perm.PERMISSION_BULK_DELETE, "name": "批量删除权限", "description": "批量删除权限项"},
        {"code": Perm.PERMISSION_DISABLE, "name": "禁用权限", "description": "禁用权限项"},
        {"code": Perm.PERMISSION_HARD_DELETE, "name": "硬删除权限", "description": "不可恢复删除权限项"},
        {"code": Perm.PERMISSION_LIST_ALL, "name": "权限全量列表", "description": "查看所有权限（含禁用/软删）"},
        {"code": Perm.LOG_LIST, "name": "审计日志列表", "description": "查看审计日志"},
        {"code": Perm.LOG_SELF, "name": "我的操作日志", "description": "查看自己的操作记录"},
        {"code": Perm.SYSTEM_CONFIG_READ, "name": "系统配置读取", "description": "读取系统配置"},
        {"code": Perm.SYSTEM_CONFIG_UPDATE, "name": "系统配置更新", "description": "更新系统配置"},
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
    """获取角色到权限编码的映射关系。

    Returns:
        dict[str, list[str]]: 角色编码 -> 权限编码列表。
    """
    perms = [p["code"] for p in get_builtin_permissions()]
    return {
        "super_admin": perms,
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


__all__ = [
    "PermissionDef",
    "RoleDef",
    "get_builtin_permissions",
    "get_builtin_roles",
    "get_role_permission_map",
]
