"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: constants.py
@DateTime: 2025/08/21 10:06:11
@Docs: 常量定义
"""

from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    USER_LIST = "user:list"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_BULK_DELETE = "user:bulk_delete"
    USER_DISABLE = "user:disable"
    USER_BIND_ROLES = "user:bind_roles"
    USER_UNBIND_ROLES = "user:unbind_roles"
    USER_BIND_ROLES_BATCH = "user:bind_roles_batch"
    USER_UNBIND_ROLES_BATCH = "user:unbind_roles_batch"

    ROLE_LIST = "role:list"
    ROLE_CREATE = "role:create"
    ROLE_UPDATE = "role:update"
    ROLE_DELETE = "role:delete"
    ROLE_BULK_DELETE = "role:bulk_delete"
    ROLE_DISABLE = "role:disable"
    ROLE_BIND_PERMISSIONS = "role:bind_permissions"
    ROLE_UNBIND_PERMISSIONS = "role:unbind_permissions"
    ROLE_BIND_PERMISSIONS_BATCH = "role:bind_permissions_batch"
    ROLE_UNBIND_PERMISSIONS_BATCH = "role:unbind_permissions_batch"

    PERMISSION_LIST = "permission:list"
    PERMISSION_CREATE = "permission:create"
    PERMISSION_UPDATE = "permission:update"
    PERMISSION_DELETE = "permission:delete"
    PERMISSION_BULK_DELETE = "permission:bulk_delete"
    PERMISSION_DISABLE = "permission:disable"

    LOG_LIST = "log:list"


__all__ = ["Permission"]
