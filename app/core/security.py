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
    # 支持 kid 轮换：优先读取 header.kid 对应密钥；如无 kid 或找不到匹配密钥，则使用默认 SECRET。
    try:
        # jose 的 decode 不提供直接读取 header 的 API，但 decode 会校验签名。
        # 我们先尝试使用 header.kid 匹配的密钥，若成功则返回；
        # 若没有 kid 或 kid 未配置，则退回默认密钥；若 kid 存在但无对应密钥，则直接判定无效，避免误用默认密钥解码。
        kid = None
        try:
            # 解析未验证的 header：jose 没有公开 API，这里使用一个轻量技巧：
            # JWT 的第一段是 header 的 base64url，无需解码库也可解析，但为简洁起见使用 jwt.get_unverified_header。
            # 注意：get_unverified_header 仅提取 header，不校验签名。
            from jose.utils import base64url_decode as _b64d  # type: ignore

            # 如果环境不支持 jose.utils（兼容处理），退回到 jose.jwt.get_unverified_header
            try:
                header_str = token.split(".", 1)[0]
                # 兼容填充
                rem = len(header_str) % 4
                if rem:
                    header_str += "=" * (4 - rem)
                import json as _json

                kid = _json.loads(_b64d(header_str.encode()).decode()).get("kid")
            except Exception:
                # 退回到 jose 的未验证 header 获取
                try:
                    header = jwt.get_unverified_header(token)
                    kid = header.get("kid") if isinstance(header, dict) else None
                except Exception:
                    kid = None
        except Exception:
            kid = None

        if kid:
            key = settings.JWT_KEYS.get(kid)
            if not key:
                raise unauthorized("令牌无效")
            return jwt.decode(token, key, algorithms=[settings.JWT_ALGORITHM])

        # 无 kid：按默认密钥解码
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
