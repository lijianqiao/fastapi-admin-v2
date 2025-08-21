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
    """抽象数据模型基类。

    提供统一的主键、启用状态、软删除、乐观锁与审计时间字段。

    Attributes:
        id (int): 主键ID（BigInt）。
        is_active (bool): 是否激活，默认 True，用于启用/停用实体。
        is_deleted (bool): 是否已软删除，默认 False。
        deleted_at (datetime | None): 软删除时间。
        version (int): 版本号（乐观锁），更新成功则自增。
        created_at (datetime): 创建时间。
        updated_at (datetime): 更新时间。

    Notes:
        - 抽象基类，不直接生成表。
        - 建议更新时配合 DAO 层的 `update_with_version` 实现乐观锁。
    """

    id = fields.BigIntField(primary_key=True, description="主键ID（BigInt）")
    is_active = fields.BooleanField(default=True, db_index=True, description="是否激活")
    is_deleted = fields.BooleanField(default=False, db_index=True, description="是否已软删除")
    deleted_at = fields.DatetimeField(null=True, description="软删除时间")
    version = fields.IntField(default=0, db_index=True, description="版本号（乐观锁）")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:  # type: ignore
        abstract = True
