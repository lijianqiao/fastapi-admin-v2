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
from app.utils.cache import close_redis
from app.utils.logger import logger, setup_logger


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    environment = settings.ENVIRONMENT
    if environment not in ("development", "testing", "production"):
        environment = "development"
    setup_logger(cast(Literal["development", "testing", "production"], environment))
    setup_middlewares(app)
    await init_database()
    logger.info("应用启动完成")
    await init_database()
    logger.info("应用启动完成")
    try:
        yield
    finally:
        await close_database()
        await close_redis()
        logger.info("应用关闭完成")


__all__ = ["lifespan", "setup_middlewares"]
