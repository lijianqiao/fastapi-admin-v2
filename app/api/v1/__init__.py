"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: __init__.py
@DateTime: 2025/08/21 12:40:00
@Docs: v1 路由聚合
"""

from __future__ import annotations

from fastapi import APIRouter

from .auth import router as auth_router
from .logs import router as logs_router
from .permissions import router as permissions_router
from .roles import router as roles_router
from .users import router as users_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
router.include_router(users_router, prefix="/users", tags=["用户管理"])
router.include_router(roles_router, prefix="/roles", tags=["角色管理"])
router.include_router(permissions_router, prefix="/permissions", tags=["权限管理"])
router.include_router(logs_router, prefix="/logs", tags=["日志管理"])

__all__ = ["router"]
