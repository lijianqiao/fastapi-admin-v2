"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: constants.py
@DateTime: 2025/08/21 10:06:11
@Docs: 枚举
"""

from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    USER_LIST = "user:list"
    USER_CREATE = "user:create"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_BULK_DELETE = "user:bulk_delete"


__all__ = ["Permission"]
