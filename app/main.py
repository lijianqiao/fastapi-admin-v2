"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: main.py
@DateTime: 2025/08/21 15:20:20
@Docs: 主应用
"""

from fastapi import FastAPI

from app.api import api_router
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.lifespan import lifespan, setup_middlewares


def create_app() -> FastAPI:
    """创建 FastAPI 应用
    Returns:
        FastAPI: FastAPI 应用
    """
    settings = get_settings()
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        debug=settings.DEBUG,
        lifespan=lifespan,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )

    # 中间件必须在应用启动前添加
    setup_middlewares(app)
    install_exception_handlers(app)

    # v1 API
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
