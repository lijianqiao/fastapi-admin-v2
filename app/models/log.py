"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: log.py
@DateTime: 2025/08/21 10:19:24
@Docs: 数据模型：操作审计日志
"""

from __future__ import annotations

from tortoise import fields

from app.models.base import BaseModel


class AuditLog(BaseModel):
    """
    数据模型：操作审计日志
    """

    actor_id = fields.BigIntField(index=True, description="操作者用户ID")
    action = fields.CharField(max_length=64, description="操作动作标识")
    target_id = fields.BigIntField(null=True, description="目标对象ID")
    path = fields.CharField(max_length=255, null=True, description="请求路径")
    method = fields.CharField(max_length=16, null=True, description="HTTP方法")
    ip = fields.CharField(max_length=64, null=True, description="客户端IP")
    ua = fields.CharField(max_length=255, null=True, description="User-Agent")
    status = fields.IntField(null=True, description="HTTP状态码")
    latency_ms = fields.IntField(null=True, description="请求耗时（毫秒）")
    trace_id = fields.CharField(max_length=64, null=True, description="Trace ID")
    error = fields.TextField(null=True, description="错误详情")

    class Meta:  # type: ignore
        table = "audit_logs"
        indexes = (
            ("actor_id", "created_at"),
            ("trace_id",),
            ("status", "created_at"),
            ("id", "version"),
        )
