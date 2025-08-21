"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025/08/21 11:20:00
@Docs: 审计日志 Schemas
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    actor_id: int
    action: str
    target_id: int | None = None
    path: str | None = None
    method: str | None = None
    ip: str | None = None
    ua: str | None = None
    status: int | None = None
    latency_ms: int | None = None
    trace_id: str | None = None
    error: str | None = None
    created_at: str


class AuditLogQuery(BaseModel):
    actor_id: int | None = None
    action: str | None = None
    trace_id: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)
