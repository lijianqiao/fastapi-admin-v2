"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permissions.py
@DateTime: 2025/08/21 12:45:00
@Docs: 权限相关 API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import get_current_user_id, get_permission_service, has_permission
from app.schemas.permission import PermissionCreate, PermissionIdsIn, PermissionOut, PermissionUpdate
from app.schemas.response import Page, Response
from app.services import PermissionService

router = APIRouter()


@router.post(
    "/",
    dependencies=[Depends(has_permission(Perm.PERMISSION_CREATE))],
    response_model=Response[PermissionOut],
    summary="创建权限",
)
async def create_permission(
    data: PermissionCreate,
    svc: PermissionService = Depends(get_permission_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[PermissionOut]:
    """创建权限。

    Args:
        data (PermissionCreate): 权限创建入参。
        svc (PermissionService): 权限服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[PermissionOut]: 统一响应包装的权限信息。
    """
    perm = await svc.create_permission(data, actor_id=actor_id)
    return Response[PermissionOut](data=perm)


@router.put(
    "/{perm_id}",
    dependencies=[Depends(has_permission(Perm.PERMISSION_UPDATE))],
    response_model=Response[None],
    summary="更新权限",
)
async def update_permission(
    perm_id: int,
    version: int = Query(..., description="乐观锁版本号"),
    data: PermissionUpdate | None = None,
    svc: PermissionService = Depends(get_permission_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """更新权限。

    Args:
        perm_id (int): 权限ID。
        version (int): 乐观锁版本号。
        data (PermissionUpdate | None): 更新入参。
        svc (PermissionService): 权限服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.update_permission(perm_id, version, data or PermissionUpdate(), actor_id=actor_id)
    return Response[None](data=None)


@router.get(
    "/{perm_id}",
    dependencies=[Depends(has_permission(Perm.PERMISSION_LIST))],
    response_model=Response[PermissionOut],
    summary="获取权限详情",
)
async def get_permission(
    perm_id: int,
    svc: PermissionService = Depends(get_permission_service),
) -> Response[PermissionOut]:
    """获取权限详情。

    Args:
        perm_id (int): 权限ID。
        svc (PermissionService): 权限服务依赖。

    Returns:
        Response[PermissionOut]: 统一响应包装的权限信息。
    """
    perm = await svc.get_permission(perm_id)
    return Response[PermissionOut](data=perm)


@router.get(
    "/",
    dependencies=[Depends(has_permission(Perm.PERMISSION_LIST))],
    response_model=Response[Page[PermissionOut]],
    summary="分页查询权限列表",
)
async def list_permissions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: PermissionService = Depends(get_permission_service),
) -> Response[Page[PermissionOut]]:
    """分页查询权限列表。

    Args:
        page (int): 页码。
        page_size (int): 每页数量。
        svc (PermissionService): 权限服务依赖。

    Returns:
        Response[Page[PermissionOut]]: 统一响应包装的分页权限列表。
    """
    result = await svc.list_permissions(page=page, page_size=page_size)
    return Response[Page[PermissionOut]](data=result)


@router.post(
    "/disable",
    dependencies=[Depends(has_permission(Perm.PERMISSION_DISABLE))],
    response_model=Response[None],
    summary="批量禁用权限",
)
async def disable_permissions(
    body: PermissionIdsIn,
    svc: PermissionService = Depends(get_permission_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """批量禁用权限。

    Args:
        body (PermissionIdsIn): 权限ID列表。
        svc (PermissionService): 权限服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.disable_permissions(body.ids, actor_id=actor_id)
    return Response[None](data=None)
