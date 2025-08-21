"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: __init__.py
@DateTime: 2025/08/21 11:20:00
@Docs: Schemas 导出
"""

from .auth import LoginIn, RefreshIn, TokenOut
from .common import Pagination
from .log import AuditLogOut, AuditLogQuery
from .permission import PermissionCreate, PermissionOut, PermissionUpdate
from .response import Page, Response
from .role import RoleBindIn, RoleCreate, RoleIdsIn, RoleOut, RoleUpdate
from .user import UserBindIn, UserCreate, UserIdsIn, UserOut, UserQuery, UserUpdate

__all__ = [
    "Response",
    "Page",
    "Pagination",
    # user
    "UserCreate",
    "UserUpdate",
    "UserOut",
    "UserQuery",
    "UserIdsIn",
    "UserBindIn",
    # role
    "RoleCreate",
    "RoleUpdate",
    "RoleOut",
    "RoleBindIn",
    "RoleIdsIn",
    # permission
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionOut",
    # log
    "AuditLogOut",
    "AuditLogQuery",
    # auth
    "LoginIn",
    "TokenOut",
    "RefreshIn",
]
