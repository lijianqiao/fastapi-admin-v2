"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: metrics.py
@DateTime: 2025/08/22 10:42:18
@Docs: Prometheus 指标与监控中间件
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

from fastapi import APIRouter, FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

from app.core.database import Tortoise

# 注册表（使用默认全局注册表即可；如需隔离可自建 CollectorRegistry）
REQUEST_COUNTER = Counter(
    "http_requests_total",
    "HTTP 请求总量",
    labelnames=("method", "path", "status"),
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "进行中的 HTTP 请求数",
    labelnames=("method", "path"),
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP 请求时延分布（秒）",
    labelnames=("method", "path"),
    buckets=(
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
        10.0,
    ),
)

DB_POOL_USAGE = Gauge(
    "db_pool_in_use",
    "数据库连接池正在使用的连接数",
)

REDIS_ERRORS = Counter(
    "redis_operation_errors_total",
    "Redis 操作失败计数",
    labelnames=("op",),
)


class MetricsMiddleware:
    """监控中间件：统计请求数量、进行中请求、时延直方图。

    使用固定 path 标签（不展开路径参数），仅取原始 path，避免高基数。
    """

    def __init__(self, app: FastAPI) -> None:
        self.app = app

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> Any:  # type: ignore[override]
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)

        method = scope.get("method", "-")
        path = scope.get("path", "-")
        start = time.perf_counter()
        REQUEST_IN_PROGRESS.labels(method, path).inc()

        status_code_holder: dict[str, int] = {"code": 500}

        async def send_wrapper(message: dict[str, Any]) -> Any:
            if message.get("type") == "http.response.start":
                status_code_holder["code"] = int(message.get("status", 500))
            return await send(message)

        try:
            return await self.app(scope, receive, send_wrapper)
        finally:
            elapsed = time.perf_counter() - start
            REQUEST_IN_PROGRESS.labels(method, path).dec()
            REQUEST_LATENCY.labels(method, path).observe(elapsed)
            REQUEST_COUNTER.labels(method, path, str(status_code_holder["code"]))
            REQUEST_COUNTER.labels(method, path, str(status_code_holder["code"])).inc()


def get_metrics_router() -> APIRouter:
    router = APIRouter(tags=["系统"])

    @router.get("/metrics")
    async def metrics(request: Request) -> Response:
        """获取指标数据
        Args:
            request (Request): 请求对象

        Returns:
            Response: 响应对象
        """
        # 简易白名单控制（生产建议用网关限制）。
        from app.core.config import get_settings as _gs

        ips = _gs().METRICS_ALLOW_IPS
        if ips:
            client_ip = request.client.host if request.client else "-"
            if client_ip not in ips:
                return Response(status_code=403)
        data = generate_latest()  # 默认全局注册表
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)

    return router


async def scrape_runtime_metrics() -> None:
    """抓取运行期指标（DB 连接池、Redis 等）。

    在请求周期外也可被调用（如定时任务）。此处为最小实现：
    - DB：统计 Tortoise 默认连接池 in_use 数（若可得）
    - Redis：仅在异常处计数（REDIS_ERRORS），无需主动抓取
    """

    try:
        conn = Tortoise.get_connection("default")  # type: ignore[attr-defined]
        pool = getattr(conn, "_pool", None)
        in_use = getattr(pool, "_holders", None)
        if in_use is not None:
            # asyncpg pool 持有者中，活跃占用可用 _holders 中 busy 标记统计；最小实现取长度
            DB_POOL_USAGE.set(len(in_use))
    except Exception:
        # 最小实现忽略错误
        pass


async def schedule_scrape_metrics(app: FastAPI) -> None:
    """周期性抓取运行态指标（后台任务）。

    仅在应用运行时循环执行，关闭时自然结束。
    Args:
        app (FastAPI): 应用对象

    Returns:
        None: 无返回
    """
    from app.core.config import get_settings as _gs

    interval = max(5, int(_gs().METRICS_SCRAPE_INTERVAL_SECONDS))
    while True:
        try:
            await scrape_runtime_metrics()
        except Exception:
            pass
        try:
            await asyncio.sleep(interval)
        except Exception:
            break


async def redis_op_with_metric(op_name: str, coro):
    """包装 Redis 操作，失败时累加错误计数。

    Args:
        op_name (str): 操作名，例如 get/set/smembers。
        coro: 原协程对象。

    Returns:
        Any: 原协程结果。
    """
    try:
        return await coro
    except Exception:
        REDIS_ERRORS.labels(op_name).inc()
        raise


__all__ = [
    "MetricsMiddleware",
    "get_metrics_router",
    "REQUEST_COUNTER",
    "REQUEST_IN_PROGRESS",
    "REQUEST_LATENCY",
    "DB_POOL_USAGE",
    "REDIS_ERRORS",
    "scrape_runtime_metrics",
    "schedule_scrape_metrics",
    "redis_op_with_metric",
]
