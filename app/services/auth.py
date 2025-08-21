"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 11:55:00
@Docs: 认证服务（登录、刷新、注销占位）
"""

from __future__ import annotations

from app.core.exceptions import unauthorized
from app.core.security import create_token_pair, verify_password
from app.dao.user import UserDAO
from app.schemas.auth import LoginIn, RefreshIn, TokenOut


class AuthService:
    def __init__(self, user_dao: UserDAO | None = None) -> None:
        self.user_dao = user_dao or UserDAO()

    async def login(self, data: LoginIn) -> TokenOut:
        # 支持 username 或 phone 登录（优先用户名）
        user = await self.user_dao.find_by_username(data.username)
        if not user:
            # 把 `username` 当作 phone 尝试
            user = await self.user_dao.find_by_phone(data.username)
        if not user or not verify_password(data.password, user.password_hash):
            raise unauthorized("用户名或密码错误")
        pair = create_token_pair(str(user.id))
        return TokenOut(**pair)

    async def refresh(self, data: RefreshIn) -> TokenOut:
        # TODO: 校验 refresh_token（黑名单/版本），此处占位直接颁发新 access_token
        # 实际实现中需要 decode + 校验 + 可能更新版本号
        return TokenOut(access_token="", token_type="bearer", refresh_token=data.refresh_token)

    async def logout(self, user_id: int) -> None:
        # TODO: 将当前用户的 token 版本提升或加入黑名单
        return None
