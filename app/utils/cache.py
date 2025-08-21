from __future__ import annotations

import redis.asyncio as redis

from app.core.config import get_settings

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """获取全局 Redis 客户端（单例）。

    Returns:
        redis.Redis: 异步 Redis 客户端。
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(get_settings().REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis() -> None:
    """关闭全局 Redis 客户端并清理单例。"""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


__all__ = ["get_redis", "close_redis"]
