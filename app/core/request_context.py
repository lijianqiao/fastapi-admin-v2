"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: request_context.py
@DateTime: 2025/08/21 14:20:00
@Docs: 请求上下文（trace_id、path、method、ip、ua）
"""

from __future__ import annotations

from contextvars import ContextVar

from app.schemas.response import RequestContext

_ctx: ContextVar[RequestContext | None] = ContextVar("request_context", default=None)


def set_request_context(ctx: RequestContext) -> None:
    """设置当前请求上下文。

    Args:
        ctx (RequestContext): 请求上下文

    Returns:
        None
    """
    _ctx.set(ctx)


def get_request_context() -> RequestContext:
    """获取当前请求上下文（未设置则返回空字典）。

    Returns:
        RequestContext: 请求上下文
    """
    val = _ctx.get()
    return val or {}


__all__ = ["RequestContext", "set_request_context", "get_request_context"]
