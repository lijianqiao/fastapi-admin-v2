"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: exceptions.py
@DateTime: 2025/08/21 09:46:00
@Docs: 自定义异常与统一异常处理器
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.utils.logger import logger


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


def install_exception_handlers(app: FastAPI) -> None:
    """安装统一异常处理器，包装为 Response 格式。

    Args:
        app (FastAPI): FastAPI 应用

    Returns:
        None: 无返回
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:  # type: ignore[override]
        """HTTP 异常处理器

        Args:
            _ (Request): 请求
            exc (StarletteHTTPException): 异常

        Returns:
            JSONResponse: 响应
        """
        # 保留原始 HTTP 状态码（如 401），响应体统一为 Response 结构
        payload = {"code": exc.status_code, "message": exc.detail or "HTTP 错误", "data": None}
        headers = getattr(exc, "headers", None)
        return JSONResponse(status_code=exc.status_code, content=payload, headers=headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:  # type: ignore[override]
        """请求验证异常处理器

        Args:
            _ (Request): 请求
            exc (RequestValidationError): 异常

        Returns:
            JSONResponse: 响应
        """

        def _to_jsonable(obj: Any) -> Any:
            # 递归转换 bytes -> str，集合 -> 列表，其他不可序列化类型转字符串
            if isinstance(obj, bytes):
                try:
                    return obj.decode("utf-8", errors="ignore")
                except Exception:  # noqa: BLE001
                    return str(obj)
            if isinstance(obj, list | tuple):
                return [_to_jsonable(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _to_jsonable(v) for k, v in obj.items()}
            if isinstance(obj, set):
                return [_to_jsonable(i) for i in obj]
            return obj

        payload = {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": "验证错误",
            "data": _to_jsonable(exc.errors()),
        }
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:  # type: ignore[override]
        """未处理异常处理器

        Args:
            _ (Request): 请求
            exc (Exception): 异常

        Returns:
            JSONResponse: 响应
        """
        logger.exception("未处理异常")
        payload = {"code": HTTP_500_INTERNAL_SERVER_ERROR, "message": "内部服务器错误", "data": None}
        return JSONResponse(status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=payload)


__all__.append("install_exception_handlers")
