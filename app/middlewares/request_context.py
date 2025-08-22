"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: request_context.py
@DateTime: 2025/08/21 14:21:00
@Docs: 请求上下文中间件：注入 trace_id 与请求元信息
"""

from __future__ import annotations

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.request_context import set_request_context
from app.utils.logger import logger


def _client_ip(request: Request) -> str | None:
    """获取客户端IP

    Args:
        request (Request): 请求对象

    Returns:
        str | None: 客户端IP
    """
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else None


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """请求上下文中间件
        Args:
            request (Request): 请求对象
            call_next (RequestResponseEndpoint): 下一个中间件

        Returns:
            Response: 响应对象
        """
        # 优先使用上游传入的 X-Request-ID（若不存在或无效则生成）
        header_rid = request.headers.get("x-request-id")
        trace_id = header_rid.strip() if header_rid else uuid.uuid4().hex
        if not trace_id:
            trace_id = uuid.uuid4().hex
        # 限制长度，避免日志注入/异常
        if len(trace_id) > 128:
            trace_id = trace_id[:128]
        path = request.url.path
        method = request.method
        ip = _client_ip(request)
        ua = request.headers.get("user-agent")

        set_request_context(
            {
                "trace_id": trace_id,
                "path": path,
                "method": method,
                "ip": ip,
                "ua": ua,
            }
        )

        # 在请求周期内注入 loguru trace_id
        with logger.contextualize(trace_id=trace_id):
            response = await call_next(request)
        # 将 trace_id 回写到响应头，便于前端/网关关联
        try:
            response.headers["X-Request-ID"] = trace_id
        except Exception:  # noqa: BLE001
            pass
        return response


__all__ = ["RequestContextMiddleware"]
