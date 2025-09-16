"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dependencies.py
@DateTime: 2025/08/21 10:05:47
@Docs: 依赖注入
"""

from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import forbidden, unauthorized
from app.core.permissions import user_has_permissions
from app.core.request_context import get_request_context
from app.core.security import decode_token
from app.dao.log import AuditLogDAO
from app.dao.permission import PermissionDAO
from app.dao.role import RoleDAO
from app.dao.role_permission import RolePermissionDAO
from app.dao.system_config import SystemConfigDAO
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.services import AuditLogService, AuthService, PermissionService, RoleService, UserService
from app.services.system_config import SystemConfigService
from app.utils.cache_manager import get_cache_manager
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
) -> int:
    """获取当前用户ID

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): 令牌
        request (Request): 请求

    Returns:
        int: 当前用户ID
    """
    # 从请求上下文获取 trace_id，避免与头部取值不一致
    ctx = get_request_context()
    trace_id = ctx.get("trace_id") or "-"
    log = logger.bind(trace_id=trace_id)

    payload = decode_token(token)
    # 令牌类型必须为 access
    typ = payload.get("typ")
    if typ != "access":
        ip = request.client.host if request.client else "-"
        log.warning(f"认证失败：令牌类型无效 typ={typ}, path={request.url.path}, ip={ip}")
        raise unauthorized("无效的访问令牌")

    subject = payload.get("sub")
    if not subject:
        ip = request.client.host if request.client else "-"
        log.warning(f"认证失败：缺少 sub，path={request.url.path}, ip={ip}")
        raise unauthorized("令牌主题无效")
    try:
        user_id = int(subject)
    except ValueError as e:
        log.warning(f"认证失败：sub 非法，sub={subject}, path={request.url.path}")
        raise unauthorized("主题格式无效") from e

    # 校验令牌版本以支持注销与强制下线
    try:
        ver_claim = int(payload.get("ver") or 0)
    except Exception:
        ver_claim = 0
    cm = get_cache_manager()
    current_ver = await cm.get_version(f"auth:ver:u:{user_id}", default=1)
    if ver_claim != current_ver:
        log.warning(
            f"认证失败：令牌版本不匹配 user_id={user_id}, token_ver={ver_claim}, current_ver={current_ver}, path={request.url.path}"
        )
        raise unauthorized("令牌已失效，请重新登录")

    return user_id


def has_permission(required: str):
    """检查用户是否有权限

    Args:
        required (str): 需要的权限

    Returns:
        None: 无返回
    """

    async def _checker(
        user_id: Annotated[int, Depends(get_current_user_id)],
        request: Request,
    ) -> None:
        ctx = get_request_context()
        trace_id = ctx.get("trace_id") or "-"
        log = logger.bind(trace_id=trace_id)

        # 状态前置校验：必须未软删且启用
        try:
            user = await UserDAO().alive().filter(id=user_id).first()
        except Exception:
            user = None
        if not user or not getattr(user, "is_active", False):
            log.warning(f"账号已禁用或不存在：user_id={user_id}, path={request.url.path}")
            raise forbidden("账号已禁用")

        req_value = getattr(required, "value", required)
        if not isinstance(req_value, str):
            req_value = str(req_value)
        allowed = await user_has_permissions(user_id, [req_value])
        if not allowed:
            log.warning(f"权限不足：user_id={user_id}, required={required}, path={request.url.path}")
            raise forbidden("权限不足")

    return _checker


# ---------- DAO Providers ----------
def get_user_dao() -> UserDAO:
    """获取用户DAO

    Returns:
        UserDAO: 用户DAO
    """
    return UserDAO()


def get_user_role_dao() -> UserRoleDAO:
    """获取用户角色DAO

    Returns:
        UserRoleDAO: 用户角色DAO
    """
    return UserRoleDAO()


def get_role_dao() -> RoleDAO:
    """获取角色DAO

    Returns:
        RoleDAO: 角色DAO
    """
    return RoleDAO()


def get_role_permission_dao() -> RolePermissionDAO:
    """获取角色权限DAO

    Returns:
        RolePermissionDAO: 角色权限DAO
    """
    return RolePermissionDAO()


def get_permission_dao() -> PermissionDAO:
    """获取权限DAO

    Returns:
        PermissionDAO: 权限DAO
    """
    return PermissionDAO()


def get_audit_log_dao() -> AuditLogDAO:
    """获取审计日志DAO

    Returns:
        AuditLogDAO: 审计日志DAO
    """
    return AuditLogDAO()


def get_system_config_dao() -> SystemConfigDAO:
    """获取系统配置DAO

    Returns:
        SystemConfigDAO: 系统配置DAO
    """
    return SystemConfigDAO()


# ---------- Service Providers ----------
def get_user_service(
    user_dao: UserDAO = Depends(get_user_dao),
    user_role_dao: UserRoleDAO = Depends(get_user_role_dao),
) -> UserService:
    """获取用户服务

    Args:
        user_dao (UserDAO): 用户DAO
        user_role_dao (UserRoleDAO): 用户角色DAO

    Returns:
        UserService: 用户服务
    """
    return UserService(user_dao=user_dao, user_role_dao=user_role_dao)


def get_role_service(
    role_dao: RoleDAO = Depends(get_role_dao),
    role_perm_dao: RolePermissionDAO = Depends(get_role_permission_dao),
    perm_dao: PermissionDAO = Depends(get_permission_dao),
) -> RoleService:
    """获取角色服务

    Args:
        role_dao (RoleDAO): 角色DAO
        role_perm_dao (RolePermissionDAO): 角色权限DAO
        perm_dao (PermissionDAO): 权限DAO

    Returns:
        RoleService: 角色服务
    """
    return RoleService(role_dao=role_dao, role_perm_dao=role_perm_dao, perm_dao=perm_dao)


def get_permission_service(
    perm_dao: PermissionDAO = Depends(get_permission_dao),
) -> PermissionService:
    """获取权限服务

    Args:
        perm_dao (PermissionDAO): 权限DAO

    Returns:
        PermissionService: 权限服务
    """
    return PermissionService(perm_dao=perm_dao)


def get_audit_log_service(
    dao: AuditLogDAO = Depends(get_audit_log_dao),
) -> AuditLogService:
    """获取审计日志服务

    Args:
        dao (AuditLogDAO): 审计日志DAO

    Returns:
        AuditLogService: 审计日志服务
    """
    return AuditLogService(dao)


def get_auth_service(
    user_dao: UserDAO = Depends(get_user_dao),
) -> AuthService:
    """获取认证服务

    Args:
        user_dao (UserDAO): 用户DAO

    Returns:
        AuthService: 认证服务
    """
    return AuthService(user_dao=user_dao)


def get_system_config_service(
    system_config_dao: SystemConfigDAO = Depends(get_system_config_dao),
) -> SystemConfigService:
    """获取系统配置服务

    Args:
        system_config_dao (SystemConfigDAO): 系统配置DAO

    Returns:
        SystemConfigService: 系统配置服务
    """
    return SystemConfigService(system_config_dao=system_config_dao)


# ---------- Dynamic defaults ----------
async def default_page_size() -> int:
    """动态默认分页大小：优先读取 SystemConfig.default_page_size。

    Args:
        None

    Returns:
        int: 默认分页大小
    """
    try:
        cfg = await SystemConfigDAO().get_singleton()
        ps = int(getattr(cfg, "default_page_size", 20) or 20)
        if ps < 1:
            return 20
        return ps
    except Exception:
        return 20


async def page_size_param(page_size: int | None = Query(None, ge=1, le=200)) -> int:
    """统一分页大小依赖

    - 若显式传入 `page_size`，使用并通过 ge/le 校验
    - 若未传入，则从系统配置读取默认分页大小，并做 1..200 的兜底裁剪
    """
    if page_size is not None:
        return page_size
    try:
        cfg = await SystemConfigDAO().get_singleton()
        ps = int(getattr(cfg, "default_page_size", 20) or 20)
    except Exception:
        ps = 20
    # 兜底裁剪，避免配置异常造成过大/过小（统一上限 200）
    if ps < 1:
        ps = 1
    if ps > 200:
        ps = 200
    return ps


__all__ = [
    "get_current_user_id",
    "has_permission",
    "oauth2_scheme",
    "default_page_size",
    "page_size_param",
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
