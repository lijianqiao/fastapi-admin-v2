"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: __init__.py
@DateTime: 2025/08/21 12:46:41
@Docs: 版本路由
"""

import datetime

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.response import Response

from .v1 import router as v1_router

api_router = APIRouter()

# 注册版本路由
api_router.include_router(v1_router, prefix="/v1")


@api_router.get("/health", tags=["系统"])
async def health_check() -> Response[dict]:
    """健康检查接口"""
    result = {
        "status": "ok",
        "version": get_settings().APP_VERSION,
        "environment": get_settings().ENVIRONMENT,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 格式化时间
    }
    return Response(data=result)


__all__ = ["v1_router"]
