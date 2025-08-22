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
    """健康检查接口（增强：DB/Redis 探活，短路超时）。"""
    import asyncio

    from app.core.database import Tortoise
    from app.utils.cache import get_redis

    async def check_db() -> bool:
        """检查数据库连接"""
        try:
            conn = Tortoise.get_connection("default")  # type: ignore[attr-defined]
            await conn.execute_query("SELECT 1;")
            return True
        except Exception:
            return False

    async def check_redis() -> bool:
        """检查 Redis 连接"""
        try:
            client = get_redis()
            pong = await client.ping()
            return bool(pong)
        except Exception:
            return False

    async def with_timeout(coro, timeout: float) -> bool:  # type: ignore[no-untyped-def]
        """设置超时"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except Exception:
            return False

    ok_db, ok_redis = await asyncio.gather(with_timeout(check_db(), 0.5), with_timeout(check_redis(), 0.3))

    result = {
        "status": "ok" if ok_db and ok_redis else "degraded",
        "db": ok_db,
        "redis": ok_redis,
        "version": get_settings().APP_VERSION,
        "environment": get_settings().ENVIRONMENT,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return Response(data=result)


__all__ = ["v1_router"]
