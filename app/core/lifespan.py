"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: lifespan.py
@DateTime: 2025/08/21 10:20:28
@Docs: 应用生命周期管理
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_database, init_database
from app.core.metrics import MetricsMiddleware, get_metrics_router, schedule_scrape_metrics, scrape_runtime_metrics
from app.core.permissions import bump_perm_version
from app.middlewares.force_https import ForceHTTPSMiddleware
from app.middlewares.rate_limit import RateLimitMiddleware
from app.middlewares.request_context import RequestContextMiddleware
from app.utils.cache import close_redis
from app.utils.logger import logger, setup_logger

settings = get_settings()


def setup_middlewares(app: FastAPI) -> None:
    """设置中间件

    Args:
        app (FastAPI): FastAPI 应用

    Returns:
        None: 无返回
    """
    app.add_middleware(
        RequestContextMiddleware,
    )

    # 强制 HTTPS（如开启）需尽早拦截
    app.add_middleware(ForceHTTPSMiddleware)

    allow_origins = settings.CORS_ALLOW_ORIGINS
    allow_credentials = settings.CORS_ALLOW_CREDENTIALS
    # 生产安全：当 allow_credentials=True 时不允许 *
    if allow_credentials and any(o == "*" for o in allow_origins):
        allow_origins = ["*"] if settings.ENVIRONMENT == "development" else []

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,  # 不再回退为 *，确保生产安全
        allow_credentials=allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 限流中间件（在日志与CORS之后、路由之前）
    app.add_middleware(RateLimitMiddleware)
    # 指标中间件
    app.add_middleware(MetricsMiddleware)
    # 暴露 /metrics
    app.include_router(get_metrics_router())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理

    Args:
        app (FastAPI): FastAPI 应用

    Returns:
        AsyncIterator[None]: 异步迭代器
    """
    environment = settings.ENVIRONMENT
    if environment not in ("development", "testing", "production"):
        environment = "development"
    setup_logger(cast(Literal["development", "testing", "production"], environment))
    await init_database()
    # 启动时抓一次运行期指标
    try:
        await scrape_runtime_metrics()
    except Exception:
        pass
    # 后台周期抓取运行期指标
    try:
        import asyncio

        app.add_event_handler("startup", lambda: None)  # 保持兼容
        asyncio.create_task(schedule_scrape_metrics(app))
    except Exception:
        pass
    logger.info("应用启动完成")
    try:
        yield
    finally:
        # 关停前提升权限版本，避免重启后命中旧缓存
        try:
            await bump_perm_version()
        except Exception:
            pass
        await close_database()
        await close_redis()
        logger.info("应用关闭完成")


__all__ = ["lifespan", "setup_middlewares"]
