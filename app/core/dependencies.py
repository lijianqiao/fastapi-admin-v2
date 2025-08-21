"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: dependencies.py
@DateTime: 2025/08/21 10:05:47
@Docs: 依赖注入
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import forbidden, unauthorized
from app.core.security import decode_token
from app.utils.logger import logger

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_id(
    token: Annotated[str, Depends(oauth2_scheme)],
    request: Request,
) -> int:
    trace_id = request.headers.get("X-Request-ID") or "-"
    log = logger.bind(trace_id=trace_id)

    payload = decode_token(token)
    subject = payload.get("sub")
    if not subject:
        ip = request.client.host if request.client else "-"
        log.warning(f"认证失败：缺少 sub，path={request.url.path}, ip={ip}")
        raise unauthorized("令牌主题无效")
    try:
        return int(subject)
    except ValueError as e:
        log.warning(f"认证失败：sub 非法，sub={subject}, path={request.url.path}")
        raise unauthorized("主题格式无效") from e


def has_permission(required: str):
    async def _checker(
        user_id: Annotated[int, Depends(get_current_user_id)],
        request: Request,
    ) -> None:
        trace_id = request.headers.get("X-Request-ID") or "-"
        log = logger.bind(trace_id=trace_id)

        # TODO: 替换为 Redis + DB 权限校验
        allowed = True
        if not allowed:
            log.warning(f"权限不足：user_id={user_id}, required={required}, path={request.url.path}")
            raise forbidden("权限不足")

    return _checker


__all__ = ["get_current_user_id", "has_permission", "oauth2_scheme"]
