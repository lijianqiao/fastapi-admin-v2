"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permissions.py
@DateTime: 2025/08/21 12:10:00
@Docs: 权限检查工具（占位：后续接入 Redis 缓存 + DB）
"""

from __future__ import annotations

from collections.abc import Iterable


async def user_has_permissions(user_id: int, required: Iterable[str]) -> bool:
    # TODO: 接入 Redis 权限缓存与 DB 聚合权限
    # 现阶段默认放行（请在集成 RBAC 时替换实现）
    return True


__all__ = ["user_has_permissions"]
