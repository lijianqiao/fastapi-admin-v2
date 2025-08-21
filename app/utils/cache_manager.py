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
    """Redis 缓存管理器。

    统一封装 Key 规范、JSON 读写、集合操作以及版本号管理。

    Attributes:
        client (redis.Redis): Redis 异步客户端。
    """

    def __init__(self, client: redis.Redis) -> None:
        """初始化缓存管理器。

        Args:
            client (redis.Redis): Redis 异步客户端。

        Returns:
            None: 无返回。
        """
        self.client = client

    # Key 构造
    @staticmethod
    def build_key(*parts: Any) -> str:
        """构造标准化的缓存 Key。

        Args:
            *parts (Any): 组成 Key 的各段。

        Returns:
            str: 以冒号连接的 Key 字符串。
        """
        return ":".join(str(p) for p in parts if p is not None and str(p) != "")

    # 基础操作
    async def get(self, key: str) -> str | None:
        """读取字符串值。

        Args:
            key (str): 键名。

        Returns:
            str | None: 字符串或 None。
        """
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int | None = DEFAULT_TTL_SECONDS) -> bool:
        """写入字符串值并设置过期。

        Args:
            key (str): 键名。
            value (str): 值。
            ttl (int | None): 过期秒数，默认 1800。

        Returns:
            bool: 是否成功。
        """
        return bool(await self.client.set(key, value, ex=ttl))

    async def delete(self, *keys: str) -> int:
        """删除一个或多个 Key。

        Args:
            *keys (str): 键名列表。

        Returns:
            int: 删除数量。
        """
        if not keys:
            return 0
        return int(await self.client.delete(*keys))

    async def exists(self, key: str) -> bool:
        """判断 Key 是否存在。

        Args:
            key (str): 键名。

        Returns:
            bool: 是否存在。
        """
        return bool(await self.client.exists(key))

    async def incr(self, key: str) -> int:
        """对 Key 自增并返回结果。

        Args:
            key (str): 键名。

        Returns:
            int: 自增后的结果。
        """
        return int(await self.client.incr(key))

    async def expire(self, key: str, ttl: int) -> bool:
        """设置 Key 过期时间。

        Args:
            key (str): 键名。
            ttl (int): 过期时间。

        Returns:
            bool: 是否成功。
        """
        return bool(await self.client.expire(key, ttl))

    # JSON 简化
    async def get_json(self, key: str) -> Any:
        """读取 JSON 值并反序列化。

        Args:
            key (str): 键名。

        Returns:
            Any: 反序列化后的值。
        """
        raw = await self.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except Exception:
            return None

    async def set_json(self, key: str, obj: Any, ttl: int | None = DEFAULT_TTL_SECONDS) -> bool:
        """序列化对象为 JSON 并写入。

        Args:
            key (str): 键名。
            obj (Any): 对象。
            ttl (int | None): 过期时间。

        Returns:
            bool: 是否成功。
        """
        return await self.set(key, json.dumps(obj, ensure_ascii=False), ttl)

    # 集合类（用于权限集合等）
    async def sadd(self, key: str, *members: str) -> int:
        """向集合添加成员。

        Args:
            key (str): 键名。
            *members (str): 成员列表。

        Returns:
            int: 添加数量。
        """
        if not members:
            return 0
        return int(await self.client.sadd(key, *members))

    async def smembers(self, key: str) -> set[str]:
        """读取集合的所有成员（字符串集合）。

        Args:
            key (str): 键名。

        Returns:
            set[str]: 集合成员。
        """
        vals = await self.client.smembers(key)
        return {v if isinstance(v, str) else v.decode("utf-8") for v in vals}

    # 版本号工具
    async def get_version(self, key: str, default: int = 1) -> int:
        """获取整数版本号，失败时返回默认值。

        Args:
            key (str): 键名。
            default (int): 默认值。

        Returns:
            int: 版本号。
        """
        val = await self.client.get(key)
        try:
            return int(val) if val is not None else default
        except Exception:
            return default

    async def bump_version(self, key: str) -> int:
        """版本号自增（返回自增后数值）。

        Args:
            key (str): 键名。

        Returns:
            int: 自增后的结果。
        """
        return int(await self.client.incr(key))

    # 扫描失效（谨慎使用）
    async def invalidate_by_pattern(self, pattern: str) -> int:
        """根据模式批量失效 Key（谨慎使用）。

        Args:
            pattern (str): 模式。

        Returns:
            int: 删除数量。
        """
        deleted = 0
        async for key in self.client.scan_iter(match=pattern, count=1000):
            deleted += int(await self.client.unlink(key))
        return deleted


_manager: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """获取全局缓存管理器实例（单例）。

    Returns:
        CacheManager: 缓存管理器。
    """
    global _manager
    if _manager is None:
        _manager = CacheManager(get_redis())
    return _manager


__all__ = ["CacheManager", "get_cache_manager", "DEFAULT_TTL_SECONDS"]
