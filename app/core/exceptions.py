"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: exceptions.py
@DateTime: 2025/08/21 10:20:17
@Docs: 自定义异常类
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


class AppError(HTTPException):
    def __init__(self, status_code: int, detail: Any = None, headers: dict[str, str] | None = None) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)


def bad_request(detail: Any = "Bad request") -> AppError:
    return AppError(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def unauthorized(detail: Any = "Unauthorized") -> AppError:
    return AppError(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def forbidden(detail: Any = "Forbidden") -> AppError:
    return AppError(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def not_found(detail: Any = "Not found") -> AppError:
    return AppError(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: Any = "Conflict") -> AppError:
    return AppError(status_code=status.HTTP_409_CONFLICT, detail=detail)


def unprocessable(detail: Any = "Unprocessable Entity") -> AppError:
    return AppError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def server_error(detail: Any = "Internal Server Error") -> AppError:
    return AppError(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


__all__ = [
    "AppError",
    "bad_request",
    "unauthorized",
    "forbidden",
    "not_found",
    "conflict",
    "unprocessable",
    "server_error",
]
