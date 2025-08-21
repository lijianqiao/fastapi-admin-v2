"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: __init__.py
@DateTime: 2025/08/21 12:46:41
@Docs: 版本路由
"""

from fastapi import APIRouter

from .v1 import router as v1_router

api_router = APIRouter()

# 注册版本路由
api_router.include_router(v1_router, prefix="/v1")

__all__ = ["v1_router"]
