"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: security.py
@DateTime: 2025/08/21 10:20:37
@Docs: 安全相关功能
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import unauthorized
from app.schemas.auth import TokenPair

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """哈希密码
    Args:
        plain_password (str): 明文密码

    Returns:
        str: 哈希密码
    """
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    Args:
        plain_password (str): 明文密码
        hashed_password (str): 哈希密码

    Returns:
        bool: 是否验证成功
    """
    return password_context.verify(plain_password, hashed_password)


def _create_token(subject: str, expires_delta: int, extra_claims: dict[str, Any] | None = None) -> str:
    """创建令牌

    Args:
        subject (str): 主题
        expires_delta (int): 过期时间
        extra_claims (dict[str, Any] | None): 额外声明

    Returns:
        str: 令牌
    """
    settings = get_settings()
    now = dt.datetime.now(dt.UTC)
    exp = now + dt.timedelta(seconds=expires_delta)
    payload: dict[str, Any] = {"sub": subject, "iat": now, "exp": exp, "ver": 1}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """创建访问令牌

    Args:
        subject (str): 主题
        extra_claims (dict[str, Any] | None): 额外声明

    Returns:
        str: 访问令牌
    """
    return _create_token(subject, get_settings().ACCESS_TOKEN_EXPIRE_SECONDS, extra_claims)


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """创建刷新令牌

    Args:
        subject (str): 主题
        extra_claims (dict[str, Any] | None): 额外声明

    Returns:
        str: 刷新令牌
    """
    return _create_token(subject, get_settings().REFRESH_TOKEN_EXPIRE_SECONDS, extra_claims)


def create_token_pair(subject: str) -> TokenPair:
    """创建令牌对

    Args:
        subject (str): 主题

    Returns:
        TokenPair: 令牌对
    """
    return {
        "access_token": create_access_token(subject),
        "refresh_token": create_refresh_token(subject),
        "token_type": "bearer",
    }


def decode_token(token: str) -> dict[str, Any]:
    """解码令牌

    Args:
        token (str): 令牌

    Returns:
        dict[str, Any]: 解码后的令牌
    """
    try:
        return jwt.decode(token, get_settings().JWT_SECRET_KEY, algorithms=[get_settings().JWT_ALGORITHM])
    except JWTError as exc:
        raise unauthorized("令牌无效") from exc


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
]
