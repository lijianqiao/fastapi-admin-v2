"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: response.py
@DateTime: 2025/08/21 11:20:00
@Docs: 统一响应与分页模型
"""

from __future__ import annotations

from typing import TypedDict, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Response[T](BaseModel):
    """统一响应模型。

    Attributes:
        code (int): 业务状态码，默认 200。
        message (str): 提示信息，默认 "success"。
        data (T | None): 业务数据载荷，泛型类型。

    Notes:
        - 除登录接口外，其他 API 均使用该响应包装。
    """

    code: int = Field(default=200)
    message: str = Field(default="success")
    data: T | None = None


class Page[T](BaseModel):
    """分页结果模型。

    Attributes:
        items (list[T]): 当前页项目列表。
        total (int): 总记录数。
        page (int): 当前页码。
        page_size (int): 每页大小。
    """

    items: list[T]
    total: int
    page: int
    page_size: int


class RequestContext(TypedDict, total=False):
    """请求上下文。

    Attributes:
        trace_id (str): 追踪ID。
        path (str | None): 请求路径。
        method (str | None): 请求方法。
        ip (str | None): 客户端IP。
        ua (str | None): User-Agent。
    """

    trace_id: str
    path: str | None
    method: str | None
    ip: str | None
    ua: str | None
