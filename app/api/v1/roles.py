"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: roles.py
@DateTime: 2025/08/21 12:45:00
@Docs: 角色相关 API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import get_current_user_id, get_role_service, has_permission
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.schemas.response import Page, Response
from app.schemas.role import RoleBindIn, RoleCreate, RoleIdsIn, RoleOut, RolesBindIn, RoleUpdate
from app.schemas.user import UserOut
from app.services import RoleService

router = APIRouter()


@router.post(
    "/", dependencies=[Depends(has_permission(Perm.ROLE_CREATE))], response_model=Response[RoleOut], summary="创建角色"
)
async def create_role(
    data: RoleCreate,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[RoleOut]:
    """创建角色。

    Args:
        data (RoleCreate): 角色创建入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[RoleOut]: 统一响应包装的角色信息。
    """
    role = await svc.create_role(data, actor_id=actor_id)
    return Response[RoleOut](data=role)


@router.put(
    "/{role_id}",
    dependencies=[Depends(has_permission(Perm.ROLE_UPDATE))],
    response_model=Response[None],
    summary="更新角色",
)
async def update_role(
    role_id: int,
    version: int = Query(..., description="乐观锁版本号"),
    data: RoleUpdate | None = None,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """更新角色。

    Args:
        role_id (int): 角色ID。
        version (int): 乐观锁版本号。
        data (RoleUpdate | None): 更新入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.update_role(role_id, version, data or RoleUpdate(), actor_id=actor_id)
    return Response[None](data=None)


@router.get(
    "/{role_id}/users",
    dependencies=[Depends(has_permission(Perm.USER_LIST))],
    response_model=Response[Page[UserOut]],
    summary="查看角色下的用户",
)
async def list_users_of_role(
    role_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    ur_dao: UserRoleDAO = Depends(),
    user_dao: UserDAO = Depends(),
) -> Response[Page[UserOut]]:
    """查看角色下的用户。
    Args:
        role_id (int): 角色ID。
        page (int): 页码。
        page_size (int): 每页数量。
        ur_dao (UserRoleDAO): 用户角色关系数据访问对象。
        user_dao (UserDAO): 用户数据访问对象。

    Returns:
        Response[Page[UserOut]]: 统一响应包装的分页用户列表。
    """
    rels = await ur_dao.list_users_of_role(role_id)
    uids = [r.user_id for r in rels]
    items = await user_dao.get_many_by_ids(uids) if uids else []
    # 简单分页（内存分页，数据量大建议改为 SQL 分页）
    start = (page - 1) * page_size
    end = start + page_size
    sel = items[start:end]
    return Response[Page[UserOut]](
        data=Page[UserOut](
            items=[UserOut.model_validate(x) for x in sel], total=len(items), page=page, page_size=page_size
        )
    )


@router.get(
    "/{role_id}",
    dependencies=[Depends(has_permission(Perm.ROLE_LIST))],
    response_model=Response[RoleOut],
    summary="获取角色详情",
)
async def get_role(
    role_id: int,
    svc: RoleService = Depends(get_role_service),
) -> Response[RoleOut]:
    """获取角色详情。

    Args:
        role_id (int): 角色ID。
        svc (RoleService): 角色服务依赖。

    Returns:
        Response[RoleOut]: 统一响应包装的角色信息。
    """
    role = await svc.get_role(role_id)
    return Response[RoleOut](data=role)


@router.get(
    "/",
    dependencies=[Depends(has_permission(Perm.ROLE_LIST))],
    response_model=Response[Page[RoleOut]],
    summary="分页查询角色列表",
)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: RoleService = Depends(get_role_service),
) -> Response[Page[RoleOut]]:
    """分页查询角色列表。

    Args:
        page (int): 页码。
        page_size (int): 每页数量。
        svc (RoleService): 角色服务依赖。

    Returns:
        Response[Page[RoleOut]]: 统一响应包装的分页角色列表。
    """
    result = await svc.list_roles(page=page, page_size=page_size)
    return Response[Page[RoleOut]](data=result)


@router.post(
    "/disable",
    dependencies=[Depends(has_permission(Perm.ROLE_DISABLE))],
    response_model=Response[None],
    summary="批量禁用角色",
)
async def disable_roles(
    body: RoleIdsIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """批量禁用角色。

    Args:
        body (RoleIdsIn): 角色ID列表。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.disable_roles(body.ids, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-permissions",
    dependencies=[Depends(has_permission(Perm.ROLE_BIND_PERMISSIONS))],
    response_model=Response[None],
    summary="为角色绑定权限",
)
async def bind_permissions(
    body: RoleBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为角色绑定权限。

    Args:
        body (RoleBindIn): 角色绑定权限入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.bind_permissions(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-permissions/batch",
    dependencies=[Depends(has_permission(Perm.ROLE_BIND_PERMISSIONS_BATCH))],
    response_model=Response[None],
    summary="为多个角色批量绑定多个权限",
)
async def bind_permissions_batch(
    body: RolesBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为多个角色批量绑定多个权限。

    Args:
        body (RolesBindIn): 角色绑定权限入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.bind_permissions_batch(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-permissions",
    dependencies=[Depends(has_permission(Perm.ROLE_UNBIND_PERMISSIONS))],
    response_model=Response[None],
    summary="为角色移除权限",
)
async def unbind_permissions(
    body: RoleBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为角色移除权限。

    Args:
        body (RoleBindIn): 角色绑定权限入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.unbind_permissions(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-permissions/batch",
    dependencies=[Depends(has_permission(Perm.ROLE_UNBIND_PERMISSIONS_BATCH))],
    response_model=Response[None],
    summary="为多个角色批量移除多个权限",
)
async def unbind_permissions_batch(
    body: RolesBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """为多个角色批量移除多个权限。

    Args:
        body (RolesBindIn): 角色绑定权限入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.unbind_permissions_batch(body, actor_id=actor_id)
    return Response[None](data=None)
