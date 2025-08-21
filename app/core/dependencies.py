"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dependencies.py
@DateTime: 2025/08/21 10:05:47
@Docs: 依赖注入
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import forbidden, unauthorized
from app.core.permissions import user_has_permissions
from app.core.security import decode_token
from app.dao.log import AuditLogDAO
from app.dao.permission import PermissionDAO
from app.dao.role import RoleDAO
from app.dao.role_permission import RolePermissionDAO
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.services import AuditLogService, AuthService, PermissionService, RoleService, UserService
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
) -> int:
    trace_id = request.headers.get("X-Request-ID") or "-"
    log = logger.bind(trace_id=trace_id)

    payload = decode_token(token)
    subject = payload.get("sub")
    if not subject:
        ip = request.client.host if request.client else "-"
        log.warning(f"认证失败：缺少 sub，path={request.url.path}, ip={ip}")
        raise unauthorized("令牌主题无效")
    try:
        return int(subject)
    except ValueError as e:
        log.warning(f"认证失败：sub 非法，sub={subject}, path={request.url.path}")
        raise unauthorized("主题格式无效") from e


def has_permission(required: str):
    async def _checker(
        user_id: Annotated[int, Depends(get_current_user_id)],
        request: Request,
    ) -> None:
        trace_id = request.headers.get("X-Request-ID") or "-"
        log = logger.bind(trace_id=trace_id)

        allowed = await user_has_permissions(user_id, [required])
        if not allowed:
            log.warning(f"权限不足：user_id={user_id}, required={required}, path={request.url.path}")
            raise forbidden("权限不足")

    return _checker


# ---------- DAO Providers ----------
def get_user_dao() -> UserDAO:
    return UserDAO()


def get_user_role_dao() -> UserRoleDAO:
    return UserRoleDAO()


def get_role_dao() -> RoleDAO:
    return RoleDAO()


def get_role_permission_dao() -> RolePermissionDAO:
    return RolePermissionDAO()


def get_permission_dao() -> PermissionDAO:
    return PermissionDAO()


def get_audit_log_dao() -> AuditLogDAO:
    return AuditLogDAO()


# ---------- Service Providers ----------
def get_user_service(
    user_dao: UserDAO = Depends(get_user_dao),
    user_role_dao: UserRoleDAO = Depends(get_user_role_dao),
) -> UserService:
    return UserService(user_dao=user_dao, user_role_dao=user_role_dao)


def get_role_service(
    role_dao: RoleDAO = Depends(get_role_dao),
    role_perm_dao: RolePermissionDAO = Depends(get_role_permission_dao),
    perm_dao: PermissionDAO = Depends(get_permission_dao),
) -> RoleService:
    return RoleService(role_dao=role_dao, role_perm_dao=role_perm_dao, perm_dao=perm_dao)


def get_permission_service(
    perm_dao: PermissionDAO = Depends(get_permission_dao),
) -> PermissionService:
    return PermissionService(perm_dao=perm_dao)


def get_audit_log_service(
    dao: AuditLogDAO = Depends(get_audit_log_dao),
) -> AuditLogService:
    return AuditLogService(dao)


def get_auth_service(
    user_dao: UserDAO = Depends(get_user_dao),
) -> AuthService:
    return AuthService(user_dao=user_dao)


__all__ = [
    "get_current_user_id",
    "has_permission",
    "oauth2_scheme",
    # dao providers
    "get_user_dao",
    "get_user_role_dao",
    "get_role_dao",
    "get_role_permission_dao",
    "get_permission_dao",
    "get_audit_log_dao",
    # service providers
    "get_user_service",
    "get_role_service",
    "get_permission_service",
    "get_audit_log_service",
    "get_auth_service",
]
