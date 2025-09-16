"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: logs.py
@DateTime: 2025/08/21 12:45:00
@Docs: 审计日志 API
"""

from fastapi import APIRouter, Depends, Query

from app.core.constants import Permission as Perm
from app.core.dependencies import get_audit_log_service, get_current_user_id, has_permission, page_size_param
from app.schemas.log import AuditLogOut, AuditLogQuery
from app.schemas.response import Page, Response
from app.services import AuditLogService

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(has_permission(Perm.LOG_LIST))],
    response_model=Response[Page[AuditLogOut]],
    summary="分页查询审计日志",
)
async def list_logs(
    actor_id: int | None = Query(None),
    action: str | None = Query(None),
    trace_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Depends(page_size_param),
    svc: AuditLogService = Depends(get_audit_log_service),
) -> Response[Page[AuditLogOut]]:
    """分页查询审计日志。

    Args:
        actor_id (int | None): 操作用户ID。
        action (str | None): 操作类型。
        trace_id (str | None): 请求追踪ID。
        page (int): 页码。
        page_size (int): 每页数量。
        svc (AuditLogService): 审计日志服务依赖。

    Returns:
        Response[Page[AuditLogOut]]: 统一响应包装的分页审计日志。
    """
    result = await svc.list_logs(
        AuditLogQuery(actor_id=actor_id, action=action, trace_id=trace_id, page=page, page_size=page_size)
    )
    return Response[Page[AuditLogOut]](data=result)


@router.get(
    "/me",
    dependencies=[Depends(has_permission(Perm.LOG_SELF))],
    response_model=Response[Page[AuditLogOut]],
    summary="查看当前用户自己的操作记录",
)
async def list_my_logs(
    page: int = Query(1, ge=1),
    page_size: int = Depends(page_size_param),
    svc: AuditLogService = Depends(get_audit_log_service),
    actor_id: int = Depends(get_current_user_id),
) -> Response[Page[AuditLogOut]]:
    """查看当前用户自己的操作记录。

    Args:
        page (int): 页码。
        page_size (int): 每页数量。
        svc (AuditLogService): 审计日志服务依赖。
        actor_id (int): 当前操作者ID。

    Returns:
        Response[Page[AuditLogOut]]: 统一响应包装的分页审计日志。
    """
    result = await svc.list_logs(
        AuditLogQuery(actor_id=actor_id, action=None, trace_id=None, page=page, page_size=page_size)
    )
    return Response[Page[AuditLogOut]](data=result)
