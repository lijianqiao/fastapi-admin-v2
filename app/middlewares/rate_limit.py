"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: rate_limit.py
@DateTime: 2025/08/22 11:10:00
@Docs: 基于 Redis 的轻量限流中间件与工具
"""

from __future__ import annotations

import time

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.core.config import get_settings
from app.utils.cache import get_redis

settings = get_settings()


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "-"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """通用限流中间件：按 IP + 路径 做每分钟请求数限制。

    - 粒度：min 级固定窗口（最小实现）。
    - 键：rl:ip:{ip}:path:{path}:m:{epoch_min}
    - 限额：Settings.RATE_LIMIT_PER_MINUTE
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        Args:
            request (Request): 请求对象
            call_next (RequestResponseEndpoint): 下一个中间件

        Returns:
            Response: 响应对象
        """
        limit = max(1, settings.RATE_LIMIT_PER_MINUTE)
        # 登录接口由专用依赖控制，不在中间件里区分
        ip = _client_ip(request)
        path = request.url.path
        now = int(time.time())
        window = now // 60
        key = f"rl:ip:{ip}:path:{path}:m:{window}"
        client = get_redis()
        try:
            c = await client.incr(key)
            if c == 1:
                await client.expire(key, 65)
            if c > limit:
                raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="请求过于频繁")
        except HTTPException:
            raise
        except Exception:
            # 限流不可用时放行（最小实现）
            pass
        return await call_next(request)


async def rate_limit_login(request: Request) -> None:
    """登录接口专用限流。

    - 维度：IP + 用户名（如果能获取 form.username）。
    - 限额：Settings.RATE_LIMIT_LOGIN_PER_MINUTE

    Args:
        request (Request): 请求对象

    Returns:
        None: 无返回
    """
    limit = max(1, settings.RATE_LIMIT_LOGIN_PER_MINUTE)
    ip = _client_ip(request)
    # 尝试从表单读取用户名
    try:
        form = await request.form()
        username_field = form.get("username")
        # 确保只对字符串类型调用strip()方法，避免UploadFile等类型的错误
        if isinstance(username_field, str):
            username = username_field.strip() or "-"
        else:
            username = "-"
    except Exception:
        username = "-"
    now = int(time.time())
    window = now // 60
    key = f"rl:login:ip:{ip}:u:{username}:m:{window}"
    client = get_redis()
    try:
        c = await client.incr(key)
        if c == 1:
            await client.expire(key, 65)
        if c > limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="登录过于频繁")
    except HTTPException:
        raise
    except Exception:
        # 限流不可用时放行
        pass


__all__ = ["RateLimitMiddleware", "rate_limit_login"]
