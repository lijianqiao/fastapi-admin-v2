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


@router.post("/login", response_model=TokenOut)
async def login(data: LoginIn, svc: AuthService = Depends(get_auth_service)) -> TokenOut:
    return await svc.login(data)


@router.post("/refresh", response_model=TokenOut)
async def refresh(data: RefreshIn, svc: AuthService = Depends(get_auth_service)) -> TokenOut:
    return await svc.refresh(data)
