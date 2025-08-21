"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025/08/21 11:40:00
@Docs: 审计日志服务
"""

from __future__ import annotations

from app.core.constants import Permission as Perm
from app.dao.log import AuditLogDAO
from app.schemas.log import AuditLogOut, AuditLogQuery
from app.schemas.response import Page
from app.services.base import BaseService
from app.utils.audit import log_operation


class AuditLogService(BaseService):
    def __init__(self, dao: AuditLogDAO | None = None) -> None:
        super().__init__(dao or AuditLogDAO())

    @log_operation(action=Perm.LOG_LIST)
    async def list_logs(self, query: AuditLogQuery, *, actor_id: int | None = None) -> Page[AuditLogOut]:
        filters: dict[str, object] = {}
        if query.actor_id is not None:
            filters["actor_id"] = query.actor_id
        if query.action:
            filters["action"] = query.action
        if query.trace_id:
            filters["trace_id"] = query.trace_id
        items, total = await self.dao.list_paginated(filters=filters, page=query.page, page_size=query.page_size)
        return Page[AuditLogOut](
            items=[AuditLogOut.model_validate(x) for x in items],
            total=total,
            page=query.page,
            page_size=query.page_size,
        )
