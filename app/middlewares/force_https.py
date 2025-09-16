"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: force_https.py
@DateTime: 2025/08/27 13:09:42
@Docs: Force HTTPS 中间件
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class ForceHTTPSMiddleware(BaseHTTPMiddleware):
    """Force HTTPS 中间件
    当系统配置开启 force_https 时，拦截非 HTTPS 请求。

    识别顺序：
        优先读取 `X-Forwarded-Proto`（反向代理场景），否则使用 request.url.scheme。

    """

    _cache_flag: bool | None = None
    _cache_expire_at: float = 0.0
    _cache_ttl_seconds: int = 10

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        # 非生产环境直接放行
        try:
            from app.core.config import get_settings

            if get_settings().ENVIRONMENT != "production":
                return await call_next(request)
        except Exception:
            # 获取环境失败时，出于稳健性选择放行
            return await call_next(request)

        # 读取 scheme
        scheme = (request.headers.get("x-forwarded-proto") or request.url.scheme or "http").lower()
        if scheme == "https":
            return await call_next(request)

        # 非 https：按系统配置决定是否拦截（带10s内存缓存）
        enabled: bool = False
        now = time.monotonic()
        try:
            if self._cache_flag is not None and now < self._cache_expire_at:
                enabled = bool(self._cache_flag)
            else:
                from app.dao.system_config import SystemConfigDAO

                dao = SystemConfigDAO()
                cfg = await dao.get_singleton()
                enabled = bool(getattr(cfg, "force_https", False))
                self._cache_flag = enabled
                self._cache_expire_at = now + self._cache_ttl_seconds
        except Exception:
            enabled = False

        if enabled:
            return JSONResponse({"code": 403, "message": "需要HTTPS", "data": None}, status_code=403)

        return await call_next(request)


__all__ = ["ForceHTTPSMiddleware"]
