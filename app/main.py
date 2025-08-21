from __future__ import annotations

from fastapi import FastAPI

from app.api.v1 import router as api_v1_router
from app.core.config import get_settings
from app.core.lifespan import lifespan, setup_middlewares


def create_app() -> FastAPI:
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

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    # v1 API
    app.include_router(api_v1_router, prefix=settings.API_PREFIX)

    return app


app = create_app()
