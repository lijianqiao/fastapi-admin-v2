"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: database.py
@DateTime: 2025/08/21 09:45:07
@Docs: tortoise-orm 数据库配置

数据迁移：
aerich init -t app.core.database.TORTOISE_ORM
aerich init-db

改动模型：
aerich migrate --name "add-indexes"
aerich upgrade
"""

from typing import Any

from tortoise import Tortoise

from app.core.config import get_settings
from app.utils.logger import logger

TORTOISE_ORM: dict[str, Any] = {
    "connections": {"default": get_settings().DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.models",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
    "use_tz": True,
    "timezone": "UTC",
}


async def init_database() -> None:
    """初始化数据库连接

    Returns:
        None: 无返回
    """
    logger.info("初始化数据库连接")
    await Tortoise.init(config=TORTOISE_ORM)
    # 测试环境自动生成表结构，避免依赖迁移
    try:
        from app.core.config import get_settings as _gs  # 延迟导入避免循环

        if _gs().ENVIRONMENT.lower() == "testing":
            await Tortoise.generate_schemas()
    except Exception:
        pass


async def close_database() -> None:
    """关闭数据库连接

    Returns:
        None: 无返回
    """
    logger.info("关闭数据库连接")
    await Tortoise.close_connections()
