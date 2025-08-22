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
from datetime import datetime
from typing import Literal

from loguru import logger

from app.core.config import get_settings


def _ensure_log_dir(path: str) -> None:
    """确保日志文件目录存在。

    Args:
        path (str): 日志文件路径。

    Returns:
        None: 无返回。
    """
    if not path:
        return
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def setup_logger(environment: Literal["development", "testing", "production"] = "development") -> None:
    """初始化 loguru 日志器。

    Args:
        environment (Literal["development", "testing", "production"]): 运行环境，影响日志级别与输出形式。

    Returns:
        None: 无返回。
    """
    logger.remove()

    # 为所有日志记录补齐 trace_id，避免 KeyError
    def _patch(record: dict) -> None:  # type: ignore[override]
        """为日志记录补齐 trace_id 字段，避免格式化 KeyError。

        Args:
            record (dict): 日志记录。

        Returns:
            None: 无返回。
        """
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

    # 文件日志（所有环境都写入文件；生产环境使用 JSON，其他环境为文本）
    # 文件名格式：logs/app_YYYY_MM_DD.log
    settings = get_settings()
    configured_path = settings.APP_LOG_PATH
    if configured_path:
        # 支持 {date} 模板
        date_str = datetime.now().strftime("%Y_%m_%d")
        log_path = configured_path.replace("{date}", date_str)
    else:
        date_str = datetime.now().strftime("%Y_%m_%d")
        log_path = f"logs/app_{date_str}.log"
    _ensure_log_dir(log_path)
    logger.add(
        log_path,
        rotation="10 MB",
        retention="15 days",
        encoding="utf-8",
        enqueue=True,
        level="DEBUG" if environment == "development" else "INFO",
        serialize=environment == "production",  # 生产环境输出 JSON
    )

    # 错误文件日志（仅记录 ERROR 及以上），单独文件，便于运维排查
    error_log_path = log_path.replace("app_", "error_")
    _ensure_log_dir(error_log_path)
    logger.add(
        error_log_path,
        rotation="10 MB",
        retention="15 days",
        encoding="utf-8",
        enqueue=True,
        level="ERROR",
        serialize=environment == "production",
    )

    # 通过 patcher 统一补全 extra 字段
    logger.configure(patcher=_patch)


__all__ = ["logger", "setup_logger"]
