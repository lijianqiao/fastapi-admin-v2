"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: users.py
@DateTime: 2025/08/21 12:45:00
@Docs: 用户相关 API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import (
    get_current_user_id,
    get_user_service,
    has_permission,
)
from app.schemas.response import Page, Response
from app.schemas.user import UserBindIn, UserCreate, UserIdsIn, UserOut, UserQuery, UsersBindIn, UserUpdate
from app.services import UserService

router = APIRouter()


@router.post("/", dependencies=[Depends(has_permission(Perm.USER_CREATE))], response_model=Response[UserOut])
async def create_user(
    data: UserCreate,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[UserOut]:
    user = await svc.create_user(data, actor_id=actor_id)
    return Response[UserOut](data=user)


@router.put("/{user_id}", dependencies=[Depends(has_permission(Perm.USER_UPDATE))], response_model=Response[None])
async def update_user(
    user_id: int,
    version: int = Query(..., description="乐观锁版本号"),
    data: UserUpdate | None = None,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.update_user(user_id, version, data or UserUpdate(), actor_id=actor_id)
    return Response[None](data=None)


@router.get("/{user_id}", dependencies=[Depends(has_permission(Perm.USER_LIST))], response_model=Response[UserOut])
async def get_user(
    user_id: int,
    svc: UserService = Depends(get_user_service),
) -> Response[UserOut]:
    user = await svc.get_user(user_id)
    return Response[UserOut](data=user)


@router.get("/", dependencies=[Depends(has_permission(Perm.USER_LIST))], response_model=Response[Page[UserOut]])
async def list_users(
    keyword: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: UserService = Depends(get_user_service),
) -> Response[Page[UserOut]]:
    result = await svc.list_users(UserQuery(keyword=keyword), page=page, page_size=page_size)
    return Response[Page[UserOut]](data=result)


@router.post("/disable", dependencies=[Depends(has_permission(Perm.USER_DISABLE))], response_model=Response[None])
async def disable_users(
    body: UserIdsIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.disable_users(body.ids, actor_id=actor_id)
    return Response[None](data=None)


@router.post("/bind-roles", dependencies=[Depends(has_permission(Perm.USER_BIND_ROLES))], response_model=Response[None])
async def bind_roles(
    body: UserBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.bind_roles(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/bind-roles/batch",
    dependencies=[Depends(has_permission(Perm.USER_BIND_ROLES_BATCH))],
    response_model=Response[None],
)
async def bind_roles_batch(
    body: UsersBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.bind_roles_batch(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-roles",
    dependencies=[Depends(has_permission(Perm.USER_UNBIND_ROLES))],
    response_model=Response[None],
)
async def unbind_roles(
    body: UserBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.unbind_roles(body, actor_id=actor_id)
    return Response[None](data=None)


@router.post(
    "/unbind-roles/batch",
    dependencies=[Depends(has_permission(Perm.USER_UNBIND_ROLES_BATCH))],
    response_model=Response[None],
)
async def unbind_roles_batch(
    body: UsersBindIn,
    svc: UserService = Depends(get_user_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[None]:
    await svc.unbind_roles_batch(body, actor_id=actor_id)
    return Response[None](data=None)
