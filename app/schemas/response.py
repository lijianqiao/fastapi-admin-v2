"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: response.py
@DateTime: 2025/08/21 11:20:00
@Docs: 统一响应与分页模型
"""

from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response[T](BaseModel):
    code: int = Field(default=200)
    message: str = Field(default="success")
    data: T | None = None


class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int
