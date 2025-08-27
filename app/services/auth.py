"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 11:55:00
@Docs: 认证服务（登录、刷新、注销占位）
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.exceptions import forbidden, unauthorized
from app.core.permissions import invalidate_user_permissions
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.dao.system_config import SystemConfigDAO
from app.dao.user import UserDAO
from app.schemas.auth import LoginIn, RefreshIn, TokenOut
from app.utils.cache_manager import get_cache_manager
from app.utils.logger import logger


def _user_ver_key(user_id: int) -> str:
    """用户令牌版本缓存键

    Args:
        user_id (int): 用户ID。

    Returns:
        str: 缓存键。
    """
    return f"auth:ver:u:{user_id}"


class AuthService:
    def __init__(self, user_dao: UserDAO | None = None) -> None:
        self.user_dao = user_dao or UserDAO()
        self._syscfg = SystemConfigDAO()

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
        # 获取 user 后优先检查禁用
        if user and not getattr(user, "is_active", True):
            logger.warning(f"登录失败：账号已禁用 user_id={user.id}")
            raise forbidden("账号已禁用")

        # 锁定检查

        if user and user.locked_until:
            locked_until = user.locked_until
            now = datetime.now(tz=UTC)
            try:
                lu = locked_until if locked_until.tzinfo else locked_until.replace(tzinfo=UTC)
            except Exception:
                lu = now
            if lu > now:
                logger.warning(f"登录失败：账号锁定中 user_id={user.id} locked_until={lu.isoformat()}")
                raise forbidden("账户已锁定，请稍后再试")

        # 校验密码；失败则累加失败次数并可能锁定
        if not user or not verify_password(data.password, user.password_hash):
            # 未找到用户：为运维日志尝试区分“已删除/不存在”，对外仍统一提示
            if not user:
                # 二次探测（包含软删）仅用于日志
                any_user = await self.user_dao.model.filter(username=data.username).first()
                if not any_user:
                    any_user = await self.user_dao.model.filter(phone=data.username).first()
                if any_user and getattr(any_user, "is_deleted", False):
                    logger.warning(f"登录失败：账号已删除 user_id={any_user.id} username_or_phone={data.username}")
                else:
                    logger.warning(f"登录失败：用户不存在 username_or_phone={data.username}")
                raise unauthorized("用户名或密码错误")

            settings = get_settings()
            cfg = None
            try:
                cfg = await self._syscfg.get_singleton()
            except Exception:
                cfg = None
            now = datetime.now(tz=UTC)
            # 如果当前仍处于锁定窗口，直接提示
            if user.locked_until:
                try:
                    lu = user.locked_until if user.locked_until.tzinfo else user.locked_until.replace(tzinfo=UTC)
                except Exception:
                    lu = now
                if lu > now:
                    raise forbidden("账户已锁定，请稍后再试")

            next_failed = (user.failed_attempts or 0) + 1
            lock_minutes = max(1, (getattr(cfg, "login_lock_minutes", 0) or settings.LOGIN_LOCK_MINUTES))
            max_attempts = max(1, (getattr(cfg, "login_max_failed_attempts", 0) or settings.LOGIN_MAX_FAILED_ATTEMPTS))
            locked_until = None
            if next_failed >= max_attempts:
                locked_until = now + timedelta(minutes=lock_minutes)
                next_failed = 0  # 锁定后重置计数
            await self.user_dao.model.filter(id=user.id).update(
                failed_attempts=next_failed,
                locked_until=locked_until,
                updated_at=now,
            )
            if locked_until:
                logger.warning(f"登录失败：连续失败触发锁定 user_id={user.id} until={locked_until.isoformat()}")
                raise forbidden("账户已锁定，请稍后再试")
            remaining = max_attempts - next_failed
            logger.warning(
                f"登录失败：密码错误 user_id={user.id} attempts={next_failed}/{max_attempts} remaining={remaining}"
            )
            raise unauthorized("用户名或密码错误")
        # 读取用户令牌版本（默认 1）
        cm = get_cache_manager()
        ver = await cm.get_version(_user_ver_key(int(user.id)), default=1)
        # 会话超时覆盖（小时）
        try:
            cfg = await self._syscfg.get_singleton()
            session_hours = int(getattr(cfg, "session_timeout_hours", 0) or 0)
        except Exception:
            session_hours = 0
        access_expires = session_hours * 3600 if session_hours > 0 else None
        access = create_access_token(
            str(user.id), extra_claims={"ver": ver, "typ": "access"}, expires_seconds=access_expires
        )
        refresh = create_refresh_token(str(user.id), extra_claims={"ver": ver, "typ": "refresh"})

        # 更新最近登录时间并清除锁定/失败计数
        now = datetime.now(tz=UTC)
        await self.user_dao.model.filter(id=user.id).update(
            last_login_at=now,
            failed_attempts=0,
            locked_until=None,
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
        # 刷新前校验账号状态（禁用/软删）——仅日志区分，对外保持统一文案
        user = await self.user_dao.get_by_id(user_id)
        if (not user) or (not getattr(user, "is_active", True)):
            logger.warning(f"刷新失败：账号已禁用或已删除 user_id={user_id}")
            raise unauthorized("令牌已失效，请重新登录")
        # 颁发新对
        # refresh 时同样应用会话超时策略
        try:
            cfg = await self._syscfg.get_singleton()
            session_hours = int(getattr(cfg, "session_timeout_hours", 0) or 0)
        except Exception:
            session_hours = 0
        access_expires = session_hours * 3600 if session_hours > 0 else None
        access = create_access_token(
            sub, extra_claims={"ver": current_ver, "typ": "access"}, expires_seconds=access_expires
        )
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
        # 清理该用户当前版本的权限集合缓存，确保退出后首次鉴权回源
        try:
            await invalidate_user_permissions(user_id)
        except Exception:
            pass
        return None
