"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: security_headers.py
@DateTime: 2025/09/17 20:00:00
@Docs: 安全响应头中间件
"""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """安全响应头中间件

    提供一组合理的默认安全响应头，默认在生产与开发均开启，具体策略可后续通过系统配置扩展。
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:  # type: ignore[override]
        response = await call_next(request)
        # 基础安全头
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        # 根据路径区分 CSP：文档页需要放宽以加载 Swagger 静态资源与内联脚本
        path = request.url.path
        try:
            from app.core.config import get_settings  # 延迟导入避免循环

            settings = get_settings()
            docs_prefix = f"{settings.API_PREFIX}/docs"
            redoc_prefix = f"{settings.API_PREFIX}/redoc"
            openapi_path = f"{settings.API_PREFIX}/openapi.json"
        except Exception:
            docs_prefix = "/docs"
            redoc_prefix = "/redoc"
            openapi_path = "/openapi.json"

        if path.startswith(docs_prefix) or path.startswith(redoc_prefix) or path == openapi_path:
            # 允许 Swagger 所需的 CDN 与内联脚本/样式
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "connect-src 'self' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "font-src 'self' data:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'"
            )
        else:
            # 默认较严格策略
            csp = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self' data:; "
                "object-src 'none'; "
                "base-uri 'self'; "
                "frame-ancestors 'none'; "
                "upgrade-insecure-requests"
            )
        response.headers.setdefault("Content-Security-Policy", csp)
        # HSTS：仅对 https 生效；由上游/force https 决定是否启用 https。
        # 这里直接下发，非 https 场景浏览器会忽略。
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        return response


__all__ = ["SecurityHeadersMiddleware"]
