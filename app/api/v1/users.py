"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: users.py
@DateTime: 2025/08/21 12:45:00
@Docs: 用户相关 API
"""

from __future__ import annotations

from fastapi import APIRouter, Body, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import (
    get_current_user_id,
    get_user_service,
    has_permission,
)
from app.schemas.response import Page, Response
from app.schemas.user import (
    AdminChangePasswordIn,
    SelfChangePasswordIn,
    UserBindIn,
    UserCreate,
    UserIdsIn,
    UserOut,
    UserQuery,
    UsersBindIn,
    UserUpdate,
)
from app.services import UserService

router = APIRouter()


@router.get(
    "/me",
    response_model=Response[UserOut],
    summary="获取当前用户详情（无需额外权限）",
)
async def get_me(
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[UserOut]:
    """获取当前用户详情（无需额外权限）。

    Args:
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[UserOut]: 统一响应包装的用户信息。
    """
    user = await svc.get_user(actor_id)
    return Response[UserOut](data=user)


@router.post(
    "/me/password",
    response_model=Response[None],
    summary="用户自助修改密码（无需权限）",
)
async def self_change_password(
    body: SelfChangePasswordIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """用户自助修改密码。

    Args:
        body (SelfChangePasswordIn): 修改密码入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.self_change_password(actor_id, body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/",
    dependencies=[Depends(has_permission(Perm.USER_CREATE))],
    response_model=Response[UserOut],
    summary="创建用户",
)
async def create_user(
    data: UserCreate,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[UserOut]:
    """创建用户。

    Args:
        data (UserCreate): 创建入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[UserOut]: 统一响应包装的用户信息。
    """
    user = await svc.create_user(data, actor_id=actor_id)
    return Response[UserOut](data=user)


@router.put(
    "/{user_id}",
    dependencies=[Depends(has_permission(Perm.USER_UPDATE))],
    response_model=Response[None],
    summary="更新用户（乐观锁）",
)
async def update_user(
    user_id: int,
    version: int = Query(..., description="乐观锁版本号"),
    data: UserUpdate = Body(default_factory=UserUpdate),
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """更新用户（乐观锁）。

    Args:
        user_id (int): 用户ID。
        version (int): 乐观锁版本号。
        data (UserUpdate | None): 更新入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.update_user(user_id, version, data, actor_id=actor_id)
    return Response[None](data=None)


@router.get(
    "/{user_id}",
    dependencies=[Depends(has_permission(Perm.USER_LIST))],
    response_model=Response[UserOut],
    summary="获取用户详情",
)
async def get_user(
    user_id: int,
    svc: UserService = Depends(get_user_service),
) -> Response[UserOut]:
    """获取用户详情。

    Args:
        user_id (int): 用户ID。
        svc (UserService): 用户服务依赖。

    Returns:
        Response[UserOut]: 统一响应包装的用户信息。
    """
    user = await svc.get_user(user_id)
    return Response[UserOut](data=user)


@router.get(
    "/",
    dependencies=[Depends(has_permission(Perm.USER_LIST))],
    response_model=Response[Page[UserOut]],
    summary="分页查询用户列表",
)
async def list_users(
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: UserService = Depends(get_user_service),
) -> Response[Page[UserOut]]:
    """分页查询用户列表。

    Args:
        keyword (str | None): 关键字。
        page (int): 页码。
        page_size (int): 每页数量。
        svc (UserService): 用户服务依赖。

    Returns:
        Response[Page[UserOut]]: 统一响应包装的分页用户列表。
    """
    result = await svc.list_users(UserQuery(keyword=keyword), page=page, page_size=page_size)
    return Response[Page[UserOut]](data=result)


@router.post(
    "/disable",
    dependencies=[Depends(has_permission(Perm.USER_DISABLE))],
    response_model=Response[None],
    summary="批量禁用用户",
)
async def disable_users(
    body: UserIdsIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """批量禁用用户。

    Args:
        body (UserIdsIn): 用户ID列表。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.disable_users(body.ids, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/{user_id}/password",
    dependencies=[Depends(has_permission(Perm.USER_UPDATE))],
    response_model=Response[None],
    summary="管理员修改指定用户密码",
)
async def admin_change_password(
    user_id: int,
    body: AdminChangePasswordIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """管理员修改指定用户密码。

    Args:
        user_id (int): 用户ID。
        body (AdminChangePasswordIn): 修改密码入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.admin_change_password(user_id, body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-roles",
    dependencies=[Depends(has_permission(Perm.USER_BIND_ROLES))],
    response_model=Response[None],
    summary="为用户绑定角色",
)
async def bind_roles(
    body: UserBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为用户绑定角色。

    Args:
        body (UserBindIn): 用户绑定角色入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.bind_roles(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-roles/batch",
    dependencies=[Depends(has_permission(Perm.USER_BIND_ROLES_BATCH))],
    response_model=Response[None],
    summary="为多个用户批量绑定角色",
)
async def bind_roles_batch(
    body: UsersBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为多个用户批量绑定多个角色。

    Args:
        body (UsersBindIn): 用户绑定角色入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.bind_roles_batch(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-roles",
    dependencies=[Depends(has_permission(Perm.USER_UNBIND_ROLES))],
    response_model=Response[None],
    summary="为用户移除角色",
)
async def unbind_roles(
    body: UserBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为用户移除角色。

    Args:
        body (UserBindIn): 用户绑定角色入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.unbind_roles(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-roles/batch",
    dependencies=[Depends(has_permission(Perm.USER_UNBIND_ROLES_BATCH))],
    response_model=Response[None],
    summary="为多个用户批量移除角色",
)
async def unbind_roles_batch(
    body: UsersBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为多个用户批量移除多个角色。

    Args:
        body (UsersBindIn): 用户绑定角色入参。
        svc (UserService): 用户服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.unbind_roles_batch(body, actor_id=actor_id)
    return Response[None](data=None)
