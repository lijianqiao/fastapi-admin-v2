"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 12:40:00
@Docs: 认证 API（登录、刷新、注销）
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.core.dependencies import get_auth_service, get_current_user_id
from app.middlewares.rate_limit import rate_limit_login
from app.schemas.auth import LoginIn, RefreshIn, TokenOut
from app.schemas.response import Response
from app.services import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenOut, summary="登录获取令牌", dependencies=[Depends(rate_limit_login)])
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    svc: AuthService = Depends(get_auth_service),
) -> TokenOut:
    """登录获取令牌。

    Args:
        form (OAuth2PasswordRequestForm): OAuth2 表单登录（username、password）。
        svc (AuthService): 认证服务依赖。

    Returns:
        TokenOut: access_token 与 refresh_token。
    """
    data = LoginIn(username=form.username, password=form.password)
    return await svc.login(data)


@router.post("/refresh", response_model=TokenOut, summary="刷新令牌")
async def refresh(data: RefreshIn, svc: AuthService = Depends(get_auth_service)) -> TokenOut:
    """刷新令牌。

    Args:
        data (RefreshIn): 刷新令牌入参。
        svc (AuthService): 认证服务依赖。

    Returns:
        TokenOut: 新的 access_token 与 refresh_token。
    """
    return await svc.refresh(data)


@router.post("/logout", response_model=None, summary="注销并使历史令牌失效")
async def logout(
    actor_id: int = Depends(get_current_user_id), svc: AuthService = Depends(get_auth_service)
) -> Response[dict]:
    """注销当前用户。

    通过提升用户的令牌版本号，使历史签发的令牌全部失效。

    Args:
        actor_id (int): 用户ID。
        svc (AuthService): 认证服务依赖。

    Returns:
        None: 无返回。
    """
    await svc.logout(actor_id)
    result = {"msg": "注销成功"}
    return Response[dict](data=result)
