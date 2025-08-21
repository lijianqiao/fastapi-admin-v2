"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 11:55:00
@Docs: 认证服务（登录、刷新、注销占位）
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.core.exceptions import forbidden, unauthorized
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.dao.user import UserDAO
from app.schemas.auth import LoginIn, RefreshIn, TokenOut
from app.utils.cache_manager import get_cache_manager


def _user_ver_key(user_id: int) -> str:
    return f"auth:ver:u:{user_id}"


class AuthService:
    def __init__(self, user_dao: UserDAO | None = None) -> None:
        self.user_dao = user_dao or UserDAO()

    async def login(self, data: LoginIn) -> TokenOut:
        """登录。

        Args:
            data (LoginIn): 登录入参。

        Returns:
            TokenOut: 令牌出参。
        """
        # 支持 username 或 phone 登录（优先用户名）
        user = await self.user_dao.find_by_username(data.username)
        if not user:
            # 把 `username` 当作 phone 尝试
            user = await self.user_dao.find_by_phone(data.username)
        # 锁定检查

        if user and user.locked_until:
            locked_until = user.locked_until
            # 兼容 naive 时间，统一按 UTC 处理
            now = datetime.now(tz=UTC)
            try:
                lu = locked_until if locked_until.tzinfo else locked_until.replace(tzinfo=UTC)
            except Exception:  # noqa: BLE001
                lu = now
            if lu > now:
                raise forbidden("账户已锁定，请稍后再试")

        if not user or not verify_password(data.password, user.password_hash):
            raise unauthorized("用户名或密码错误")
        # 读取用户令牌版本（默认 1）
        cm = get_cache_manager()
        ver = await cm.get_version(_user_ver_key(int(user.id)), default=1)
        access = create_access_token(str(user.id), extra_claims={"ver": ver, "typ": "access"})
        refresh = create_refresh_token(str(user.id), extra_claims={"ver": ver, "typ": "refresh"})

        # 更新最近登录时间并重置失败计数
        now = datetime.now(tz=UTC)
        # 直接更新，带 updated_at
        await self.user_dao.model.filter(id=user.id).update(
            last_login_at=now,
            failed_attempts=0,
            updated_at=now,
        )
        return TokenOut(access_token=access, refresh_token=refresh)

    async def refresh(self, data: RefreshIn) -> TokenOut:
        """刷新令牌。

        Args:
            data (RefreshIn): 刷新令牌入参。

        Returns:
            TokenOut: 令牌出参。
        """
        payload = decode_token(data.refresh_token)
        if payload.get("typ") != "refresh":
            raise unauthorized("无效的刷新令牌")
        sub = payload.get("sub")
        ver = int(payload.get("ver") or 0)
        if not sub or not isinstance(sub, str):
            raise unauthorized("刷新令牌无效")
        user_id = int(sub)
        cm = get_cache_manager()
        current_ver = await cm.get_version(_user_ver_key(user_id), default=1)
        if ver != current_ver:
            raise unauthorized("令牌已失效，请重新登录")
        # 颁发新对
        access = create_access_token(sub, extra_claims={"ver": current_ver, "typ": "access"})
        refresh = create_refresh_token(sub, extra_claims={"ver": current_ver, "typ": "refresh"})
        return TokenOut(access_token=access, refresh_token=refresh)

    async def logout(self, user_id: int) -> None:
        """注销。

        Args:
            user_id (int): 用户ID。
        """
        # 提升用户版本号，令历史令牌全部失效
        cm = get_cache_manager()
        await cm.bump_version(_user_ver_key(user_id))
        return None
