"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: logs.py
@DateTime: 2025/08/21 12:45:00
@Docs: 审计日志 API
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import get_audit_log_service, has_permission
from app.schemas.log import AuditLogOut, AuditLogQuery
from app.schemas.response import Page, Response
from app.services import AuditLogService

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(has_permission(Perm.LOG_LIST))],
    response_model=Response[Page[AuditLogOut]],
)
async def list_logs(
    actor_id: int | None = Query(None),
    action: str | None = Query(None),
    trace_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    svc: AuditLogService = Depends(get_audit_log_service),
) -> Response[Page[AuditLogOut]]:
    result = await svc.list_logs(
        AuditLogQuery(actor_id=actor_id, action=action, trace_id=trace_id, page=page, page_size=page_size)
    )
    return Response[Page[AuditLogOut]](data=result)
