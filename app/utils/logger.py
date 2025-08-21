"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: logger.py
@DateTime: 2025/08/21 09:27:00
@Docs: 应用日志管理器
"""

from __future__ import annotations

import os
import sys
from typing import Literal

from loguru import logger


def _ensure_log_dir(path: str) -> None:
    if not path:
        return
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def setup_logger(environment: Literal["development", "testing", "production"] = "development") -> None:
    logger.remove()

    # 为所有日志记录补齐 trace_id，避免 KeyError
    def _patch(record: dict) -> None:  # type: ignore[override]
        record.setdefault("extra", {})
        record["extra"].setdefault("trace_id", "-")

    # 控制台输出（开发环境更友好）
    logger.add(
        sys.stdout,
        level="DEBUG" if environment == "development" else "INFO",
        enqueue=True,
        backtrace=environment == "development",
        diagnose=environment == "development",
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level}</level> | <cyan>{extra[trace_id]}</cyan> | <level>{message}</level>",
    )

    # 生产环境文件日志（滚动 + 保留）
    if environment == "production":
        log_path = os.getenv("APP_LOG_PATH", "logs/app.log")
        _ensure_log_dir(log_path)
        logger.add(
            log_path,
            rotation="10 MB",
            retention="30 days",
            encoding="utf-8",
            enqueue=True,
            level="INFO",
            serialize=True,  # JSON 输出
        )

    # 通过 patcher 统一补全 extra 字段
    logger.configure(patcher=_patch)


__all__ = ["logger", "setup_logger"]
