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
    """400 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 400 错误
    """
    return AppError(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def unauthorized(detail: Any = "Unauthorized") -> AppError:
    """401 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 401 错误
    """
    return AppError(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers={"WWW-Authenticate": "Bearer"})


def forbidden(detail: Any = "Forbidden") -> AppError:
    """403 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 403 错误
    """
    return AppError(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


def not_found(detail: Any = "Not found") -> AppError:
    """404 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 404 错误
    """
    return AppError(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def conflict(detail: Any = "Conflict") -> AppError:
    """409 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 409 错误
    """
    return AppError(status_code=status.HTTP_409_CONFLICT, detail=detail)


def unprocessable(detail: Any = "Unprocessable Entity") -> AppError:
    """422 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 422 错误
    """
    return AppError(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


def server_error(detail: Any = "Internal Server Error") -> AppError:
    """500 错误

    Args:
        detail (Any): 错误详情

    Returns:
        AppError: 500 错误
    """
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
            # 递归转换：bytes/异常为 str，集合 -> 列表，保持 JSON 可序列化
            if isinstance(obj, bytes):
                try:
                    return obj.decode("utf-8", errors="ignore")
                except Exception:  # noqa: BLE001
                    return str(obj)
            if isinstance(obj, BaseException):
                return str(obj)
            if isinstance(obj, list | tuple):
                return [_to_jsonable(i) for i in obj]
            if isinstance(obj, dict):
                return {k: _to_jsonable(v) for k, v in obj.items()}
            if isinstance(obj, set):
                return [_to_jsonable(i) for i in obj]
            return obj

        def _simplify_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
            """简化错误信息

            Args:
                errors (list[dict[str, Any]]): 错误信息

            Returns:
                list[dict[str, Any]]: 简化后的错误信息
            """
            simple: list[dict[str, Any]] = []
            for e in errors:
                etype = str(e.get("type") or "validation_error")
                loc = e.get("loc") or []
                field = ".".join([str(x) for x in loc[1:]]) if isinstance(loc, list | tuple) else str(loc)
                msg = str(e.get("msg") or "参数不合法")
                ctx = e.get("ctx") or {}
                # 友好映射
                if etype == "string_too_short" and ctx.get("min_length"):
                    msg = f"{field or '字段'}长度至少 {ctx['min_length']} 位"
                if etype.startswith("value_error"):
                    # 来自 model_validator 的 ValueError 文本
                    msg = str(e.get("msg") or ctx.get("error") or "参数不合法")
                simple.append({"field": field, "message": msg, "type": etype})
            return simple

        raw_errors = exc.errors()
        friendly = _simplify_errors(_to_jsonable(raw_errors))  # type: ignore[arg-type]
        top_msg = friendly[0]["message"] if friendly else "验证失败"

        payload = {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": top_msg,
            "data": friendly,
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
