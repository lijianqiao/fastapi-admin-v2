"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025/08/21 11:05:00
@Docs: 审计日志 DAO
"""

from typing import Any

from app.dao.base import BaseDAO
from app.models import AuditLog


class AuditLogDAO(BaseDAO[AuditLog]):
    """审计日志数据访问对象。"""

    def __init__(self) -> None:
        super().__init__(AuditLog)

    async def write(self, data: dict[str, Any]) -> AuditLog:
        """写入一条审计日志。

        Args:
            data (dict[str, Any]): 日志字段字典，需包含最小字段如 `actor_id`、`action` 等。

        Returns:
            AuditLog: 新建日志实体。
        """
        return await self.create(data)
