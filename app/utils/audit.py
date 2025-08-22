"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: audit.py
@DateTime: 2025/08/21 12:10:00
@Docs: 审计日志装饰器与工具
"""

from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar

from app.core.request_context import get_request_context
from app.dao.log import AuditLogDAO
from app.utils.logger import logger

P = ParamSpec("P")
R = TypeVar("R")


def log_operation(
    *,
    action: str,
    target_getter: Callable[[tuple[Any, ...], dict[str, Any]], int | None] | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """审计日志装饰器：记录服务层操作。

    Args:
        action (str): 操作动作标识（如 "user:create"）。
        target_getter (Callable | None): 从 (args, kwargs) 中提取 target_id 的函数，可选。

    Returns:
        Callable: 装饰后的异步函数。

    Notes:
        - actor_id 从被调用函数的 kwargs 中读取（key: actor_id），缺省为 0。
        - 无论成功或失败均会写入审计日志，失败时记录异常文本。
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            started_at = time.monotonic()
            actor_id = int(kwargs.get("actor_id") or 0)
            target_id = target_getter(args, kwargs) if target_getter else None
            dao = AuditLogDAO()
            error_text: str | None = None
            status_code: int | None = 200
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as exc:
                error_text = str(exc)
                status_code = 500
                # 对预期业务冲突（409）记录为 warning，避免污染 error 日志
                from app.core.exceptions import AppError

                if isinstance(exc, AppError) and getattr(exc, "status_code", 500) == 409:
                    logger.warning(
                        f"业务冲突: action={action}, actor_id={actor_id}, target_id={target_id}, detail={error_text}"
                    )
                else:
                    logger.exception(f"操作失败: action={action}, actor_id={actor_id}, target_id={target_id}")
                raise
            finally:
                latency_ms = int((time.monotonic() - started_at) * 1000)
                try:
                    ctx = get_request_context()
                    await dao.write(
                        {
                            "actor_id": actor_id,
                            "action": action,
                            "target_id": target_id,
                            "path": ctx.get("path"),
                            "method": ctx.get("method"),
                            "ip": ctx.get("ip"),
                            "ua": ctx.get("ua"),
                            "status": status_code,
                            "latency_ms": latency_ms,
                            "trace_id": ctx.get("trace_id") or "-",
                            "error": error_text,
                        }
                    )
                except Exception:  # noqa: BLE001 - 审计失败仅记录日志
                    logger.exception("写入审计日志失败")

        return wrapper

    return decorator


__all__ = ["log_operation"]
