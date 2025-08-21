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
from app.schemas.response import Page, Response
from app.schemas.role import RoleBindIn, RoleCreate, RoleIdsIn, RoleOut, RolesBindIn, RoleUpdate
from app.services import RoleService

router = APIRouter()


@router.post("/", dependencies=[Depends(has_permission(Perm.ROLE_CREATE))], response_model=Response[RoleOut])
async def create_role(
    data: RoleCreate,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[RoleOut]:
    role = await svc.create_role(data, actor_id=actor_id)
    return Response[RoleOut](data=role)


@router.put("/{role_id}", dependencies=[Depends(has_permission(Perm.ROLE_UPDATE))], response_model=Response[None])
async def update_role(
    role_id: int,
    version: int = Query(..., description="乐观锁版本号"),
    data: RoleUpdate | None = None,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.update_role(role_id, version, data or RoleUpdate(), actor_id=actor_id)
    return Response[None](data=None)


@router.get("/{role_id}", dependencies=[Depends(has_permission(Perm.ROLE_LIST))], response_model=Response[RoleOut])
async def get_role(
    role_id: int,
    svc: RoleService = Depends(get_role_service),
) -> Response[RoleOut]:
    role = await svc.get_role(role_id)
    return Response[RoleOut](data=role)


@router.get("/", dependencies=[Depends(has_permission(Perm.ROLE_LIST))], response_model=Response[Page[RoleOut]])
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: RoleService = Depends(get_role_service),
) -> Response[Page[RoleOut]]:
    result = await svc.list_roles(page=page, page_size=page_size)
    return Response[Page[RoleOut]](data=result)


@router.post(
    "/disable",
    dependencies=[Depends(has_permission(Perm.ROLE_DISABLE))],
    response_model=Response[None],
)
async def disable_roles(
    body: RoleIdsIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.disable_roles(body.ids, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-permissions",
    dependencies=[Depends(has_permission(Perm.ROLE_BIND_PERMISSIONS))],
    response_model=Response[None],
)
async def bind_permissions(
    body: RoleBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.bind_permissions(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-permissions/batch",
    dependencies=[Depends(has_permission(Perm.ROLE_BIND_PERMISSIONS_BATCH))],
    response_model=Response[None],
)
async def bind_permissions_batch(
    body: RolesBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.bind_permissions_batch(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-permissions",
    dependencies=[Depends(has_permission(Perm.ROLE_UNBIND_PERMISSIONS))],
    response_model=Response[None],
)
async def unbind_permissions(
    body: RoleBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.unbind_permissions(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-permissions/batch",
    dependencies=[Depends(has_permission(Perm.ROLE_UNBIND_PERMISSIONS_BATCH))],
    response_model=Response[None],
)
async def unbind_permissions_batch(
    body: RolesBindIn,
    svc: RoleService = Depends(get_role_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.unbind_permissions_batch(body, actor_id=actor_id)
    return Response[None](data=None)
