"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025/08/21 11:05:00
@Docs: 审计日志 DAO
"""

from __future__ import annotations

from typing import Any

from app.dao.base import BaseDAO
from app.models import AuditLog


class AuditLogDAO(BaseDAO[AuditLog]):
    def __init__(self) -> None:
        super().__init__(AuditLog)

    async def write(self, data: dict[str, Any]) -> AuditLog:
        return await self.create(data)
