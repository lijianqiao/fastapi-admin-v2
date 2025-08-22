"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: common.py
@DateTime: 2025/08/21 11:20:00
@Docs: 通用查询与分页入参
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """通用分页入参。

    Attributes:
        page (int): 页码，从 1 开始。
        page_size (int): 每页条数，默认 20，最大 200。
    """

    page: int = Field(default=1, ge=1, description="页码，从1开始")
    page_size: int = Field(default=20, ge=1, le=200, description="分页大小")


class BindStats(BaseModel):
    """绑定/解绑统计。

    Attributes:
        added (int): 新增绑定数量。
        restored (int): 恢复软删数量。
        existed (int): 已存在且未软删的数量。
    """

    added: int = Field(default=0)
    restored: int = Field(default=0)
    existed: int = Field(default=0)
