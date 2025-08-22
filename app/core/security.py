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
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import unauthorized
from app.schemas.auth import TokenPair

settings = get_settings()

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
    now = dt.datetime.now(dt.UTC)
    exp = now + dt.timedelta(seconds=expires_delta)
    payload: dict[str, Any] = {"sub": subject, "iat": now, "exp": exp, "ver": 1}
    if extra_claims:
        payload.update(extra_claims)
    # kid 支持：若配置了 ACTIVE_KID 且在 JWT_KEYS 中，优先使用该 secret 并写入 kid
    key = settings.JWT_SECRET_KEY
    headers: dict[str, Any] | None = None
    if settings.JWT_ACTIVE_KID and settings.JWT_KEYS.get(settings.JWT_ACTIVE_KID):
        key = settings.JWT_KEYS[settings.JWT_ACTIVE_KID]
        headers = {"kid": settings.JWT_ACTIVE_KID}
    return jwt.encode(payload, key, algorithm=settings.JWT_ALGORITHM, headers=headers)


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
    # 支持 kid 轮换：带 kid 则按 kid 解；否则按默认 SECRET
    try:
        # jose 不暴露 decode headers API，采用两段式：先不校验取 header（轻量）
        # 这里最小实现：尝试使用 ACTIVE_KID 对应 key 校验一次，失败再退回默认 SECRET
        if settings.JWT_ACTIVE_KID and settings.JWT_KEYS.get(settings.JWT_ACTIVE_KID):
            try:
                return jwt.decode(
                    token, settings.JWT_KEYS[settings.JWT_ACTIVE_KID], algorithms=[settings.JWT_ALGORITHM]
                )
            except Exception:
                pass
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except ExpiredSignatureError as exc:
        raise unauthorized("令牌已过期") from exc
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
