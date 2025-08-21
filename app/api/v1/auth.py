"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 12:40:00
@Docs: 认证 API（登录、刷新、注销）
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_auth_service
from app.schemas.auth import LoginIn, RefreshIn, TokenOut
from app.services import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenOut, summary="登录获取令牌")
async def login(data: LoginIn, svc: AuthService = Depends(get_auth_service)) -> TokenOut:
    """登录获取令牌。

    Args:
        data (LoginIn): 登录凭证。
        svc (AuthService): 认证服务依赖。

    Returns:
        TokenOut: access_token 与 refresh_token。
    """
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
async def logout(user_id: int, svc: AuthService = Depends(get_auth_service)) -> None:
    """注销当前用户。

    通过提升用户的令牌版本号，使历史签发的令牌全部失效。

    Args:
        user_id (int): 用户ID。
        svc (AuthService): 认证服务依赖。

    Returns:
        None: 无返回。
    """
    await svc.logout(user_id)
    return None
