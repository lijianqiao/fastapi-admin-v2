"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: security.py
@DateTime: 2025/08/21 10:20:37
@Docs: 安全相关功能
"""

from __future__ import annotations

import datetime as dt
from typing import Any, TypedDict

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import unauthorized

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return password_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


class TokenPair(TypedDict):
    access_token: str
    refresh_token: str
    token_type: str


def _create_token(subject: str, expires_delta: int, extra_claims: dict[str, Any] | None = None) -> str:
    settings = get_settings()
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(seconds=expires_delta)
    payload: dict[str, Any] = {"sub": subject, "iat": now, "exp": exp, "ver": 1}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return _create_token(subject, get_settings().ACCESS_TOKEN_EXPIRE_SECONDS, extra_claims)


def create_refresh_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return _create_token(subject, get_settings().REFRESH_TOKEN_EXPIRE_SECONDS, extra_claims)


def create_token_pair(subject: str) -> TokenPair:
    return {
        "access_token": create_access_token(subject),
        "refresh_token": create_refresh_token(subject),
        "token_type": "bearer",
    }


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, get_settings().JWT_SECRET_KEY, algorithms=[get_settings().JWT_ALGORITHM])
    except JWTError as exc:
        raise unauthorized("Invalid token") from exc


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "decode_token",
]
