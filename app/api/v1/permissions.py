"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permissions.py
@DateTime: 2025/08/21 12:45:00
@Docs: 权限相关 API
"""

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import get_current_user_id, get_permission_service, has_permission, page_size_param
from app.dao.role import RoleDAO
from app.dao.role_permission import RolePermissionDAO
from app.schemas.permission import PermissionCreate, PermissionIdsIn, PermissionOut, PermissionUpdate
from app.schemas.response import Page, Response
from app.schemas.role import RoleOut
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
    data: PermissionUpdate,
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
    await svc.update_permission(perm_id, data, actor_id=actor_id)
    return Response[None](data=None)


@router.get(
    "/{perm_id}/roles",
    dependencies=[Depends(has_permission(Perm.ROLE_LIST))],
    response_model=Response[Page[RoleOut]],
    summary="查看权限下的角色",
)
async def list_roles_of_permission(
    perm_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Depends(page_size_param),
    rp_dao: RolePermissionDAO = Depends(),
    role_dao: RoleDAO = Depends(),
) -> Response[Page[RoleOut]]:
    """查看权限下的角色。
    Args:
        perm_id (int): 权限ID。
        page (int): 页码。
        page_size (int): 每页数量。
        rp_dao (RolePermissionDAO): 角色权限关系数据访问对象。
        role_dao (RoleDAO): 角色数据访问对象。
    Returns:
        Response[Page[RoleOut]]: 统一响应包装的分页角色列表。
    """
    # SQL 分页：按关系表分页获取 role_id，再批量查询角色详情
    base_q = rp_dao.alive().filter(permission_id=perm_id)
    total = await base_q.count()
    offset = (page - 1) * page_size
    rid_list = await base_q.order_by("-id").offset(offset).limit(page_size).values_list("role_id", flat=True)
    roles = await role_dao.get_many_by_ids(rid_list) if rid_list else []
    role_map = {int(r.id): r for r in roles}
    ordered = [role_map[rid] for rid in rid_list if rid in role_map]
    return Response[Page[RoleOut]](
        data=Page[RoleOut](
            items=[RoleOut.model_validate(x) for x in ordered], total=total, page=page, page_size=page_size
        )
    )


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
    page_size: int = Depends(page_size_param),
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


@router.delete(
    "/{perm_id}",
    dependencies=[Depends(has_permission(Perm.PERMISSION_DELETE))],
    response_model=Response[None],
    summary="删除权限（默认软删，hard=True 为硬删）",
)
async def delete_permission(
    perm_id: int,
    hard: bool = Query(False),
    svc: PermissionService = Depends(get_permission_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """删除权限（默认软删，hard=True 为硬删）。

    Args:
        perm_id (int): 权限ID。
        hard (bool): 是否硬删（默认软删）。
        svc (PermissionService): 权限服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.delete_permission(perm_id, hard=hard, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/delete",
    dependencies=[Depends(has_permission(Perm.PERMISSION_BULK_DELETE))],
    response_model=Response[None],
    summary="批量删除权限（支持 hard）",
)
async def delete_permissions(
    body: PermissionIdsIn,
    hard: bool = Query(False),
    svc: PermissionService = Depends(get_permission_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """批量删除权限。通过 `hard` 决定软删/硬删（默认软删）。

    Args:
        body (PermissionIdsIn): 权限ID列表。
        hard (bool): 是否硬删（默认软删）。
        svc (PermissionService): 权限服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.delete_permissions(body.ids, hard=hard, actor_id=actor_id)
    return Response[None](data=None)
