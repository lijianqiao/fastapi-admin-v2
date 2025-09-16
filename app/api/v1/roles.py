"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: roles.py
@DateTime: 2025/08/21 12:45:00
@Docs: 角色相关 API
"""

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import (
    get_current_user_id,
    get_role_service,
    has_permission,
    page_size_param,
)
from app.dao.user import UserDAO
from app.dao.user_role import UserRoleDAO
from app.schemas.common import BindStats
from app.schemas.response import Page, Response
from app.schemas.role import RoleBindIn, RoleCreate, RoleIdsIn, RoleOut, RoleUpdate
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
    data: RoleUpdate,
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
    await svc.update_role(role_id, data, actor_id=actor_id)
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
    page_size: int = Depends(page_size_param),
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
    # SQL 分页：先统计总数，再按关系表分页取用户ID，再批量查询用户详情
    base_q = ur_dao.alive().filter(role_id=role_id)
    total = await base_q.count()
    offset = (page - 1) * page_size
    # 先取分页后的 user_id 列表
    uid_list = await base_q.order_by("-id").offset(offset).limit(page_size).values_list("user_id", flat=True)
    users = await user_dao.get_many_by_ids(uid_list) if uid_list else []
    # 保持与 uid_list 相同顺序
    user_map = {int(u.id): u for u in users}
    ordered = [user_map[uid] for uid in uid_list if uid in user_map]
    return Response[Page[UserOut]](
        data=Page[UserOut](
            items=[UserOut.model_validate(x) for x in ordered], total=total, page=page, page_size=page_size
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
    page_size: int = Depends(page_size_param),
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


@router.delete(
    "/{role_id}",
    dependencies=[Depends(has_permission(Perm.ROLE_DELETE))],
    response_model=Response[None],
    summary="删除角色（默认软删，hard=True 为硬删）",
)
async def delete_role(
    role_id: int,
    hard: bool = Query(False),
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """删除角色（默认软删，hard=True 为硬删）。

    Args:
        role_id (int): 角色ID。
        hard (bool): 是否硬删（默认软删）。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.delete_role(role_id, hard=hard, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/delete",
    dependencies=[Depends(has_permission(Perm.ROLE_BULK_DELETE))],
    response_model=Response[None],
    summary="批量删除角色（支持 hard）",
)
async def delete_roles(
    body: RoleIdsIn,
    hard: bool = Query(False),
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    """批量删除角色。通过 `hard` 决定软删/硬删（默认软删）。

    Args:
        body (RoleIdsIn): 角色ID列表。
        hard (bool): 是否硬删（默认软删）。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    await svc.delete_roles(body.ids, hard=hard, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-permissions",
    dependencies=[Depends(has_permission(Perm.ROLE_BIND_PERMISSIONS))],
    response_model=Response[BindStats],
    summary="为角色绑定权限",
)
async def bind_permissions(
    body: RoleBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[BindStats]:
    """为角色绑定权限。

    Args:
        body (RoleBindIn): 角色绑定权限入参。
        svc (RoleService): 角色服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[None]: 统一响应包装的空数据。
    """
    stats = await svc.bind_permissions(body, actor_id=actor_id)
    return Response[BindStats](data=stats)


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
