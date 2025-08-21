"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025/08/21 10:19:12
@Docs: 数据模型基类
"""

from __future__ import annotations

from tortoise import fields
from tortoise.models import Model


class BaseModel(Model):
    """
    数据模型基类：提供统一的主键、审计与并发控制字段。
    """

    id = fields.BigIntField(pk=True, description="主键ID（BigInt）")
    is_active = fields.BooleanField(default=True, index=True, description="是否激活")
    is_deleted = fields.BooleanField(default=False, index=True, description="是否已软删除")
    deleted_at = fields.DatetimeField(null=True, description="软删除时间")
    version = fields.IntField(default=0, index=True, description="版本号（乐观锁）")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:  # type: ignore
        abstract = True
