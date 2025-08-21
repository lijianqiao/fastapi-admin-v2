"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: cache_manager.py
@DateTime: 2025/08/21 12:28:00
@Docs: Redis 缓存管理器：封装统一的 Key 规范、JSON 序列化、版本号与失效工具
"""

from __future__ import annotations

import json
from typing import Any, Final

import redis.asyncio as redis

from app.utils.cache import get_redis

DEFAULT_TTL_SECONDS: Final[int] = 1800


class CacheManager:
    def __init__(self, client: redis.Redis) -> None:
        self.client = client

    # Key 构造
    @staticmethod
    def build_key(*parts: Any) -> str:
        return ":".join(str(p) for p in parts if p is not None and str(p) != "")

    # 基础操作
    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int | None = DEFAULT_TTL_SECONDS) -> bool:
        return bool(await self.client.set(key, value, ex=ttl))

    async def delete(self, *keys: str) -> int:
        if not keys:
            return 0
        return int(await self.client.delete(*keys))

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def incr(self, key: str) -> int:
        return int(await self.client.incr(key))

    async def expire(self, key: str, ttl: int) -> bool:
        return bool(await self.client.expire(key, ttl))

    # JSON 简化
    async def get_json(self, key: str) -> Any:
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_json(self, key: str, obj: Any, ttl: int | None = DEFAULT_TTL_SECONDS) -> bool:
        return await self.set(key, json.dumps(obj, ensure_ascii=False), ttl)

    # 集合类（用于权限集合等）
    async def sadd(self, key: str, *members: str) -> int:
        if not members:
            return 0
        return int(await self.client.sadd(key, *members))

    async def smembers(self, key: str) -> set[str]:
        vals = await self.client.smembers(key)
        return {v if isinstance(v, str) else v.decode("utf-8") for v in vals}

    # 版本号工具
    async def get_version(self, key: str, default: int = 1) -> int:
        val = await self.client.get(key)
        try:
            return int(val) if val is not None else default
        except Exception:
            return default

    async def bump_version(self, key: str) -> int:
        return int(await self.client.incr(key))

    # 扫描失效（谨慎使用）
    async def invalidate_by_pattern(self, pattern: str) -> int:
        deleted = 0
        async for key in self.client.scan_iter(match=pattern, count=1000):
            deleted += int(await self.client.unlink(key))
        return deleted


_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    global _manager
    if _manager is None:
        _manager = CacheManager(get_redis())
    return _manager


__all__ = ["CacheManager", "get_cache_manager", "DEFAULT_TTL_SECONDS"]
