"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: lifespan.py
@DateTime: 2025/08/21 10:20:28
@Docs: 应用生命周期管理
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import close_database, init_database
from app.core.metrics import MetricsMiddleware, get_metrics_router, scrape_runtime_metrics
from app.middlewares.request_context import RequestContextMiddleware
from app.utils.cache import close_redis
from app.utils.logger import logger, setup_logger


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
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
    settings = get_settings()
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
    logger.info("应用启动完成")
    try:
        yield
    finally:
        await close_database()
        await close_redis()
        logger.info("应用关闭完成")


__all__ = ["lifespan", "setup_middlewares"]
