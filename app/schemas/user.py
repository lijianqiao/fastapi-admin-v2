"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:20:00
@Docs: 用户相关 Schemas
"""

from datetime import datetime

import phonenumbers
from pydantic import BaseModel, EmailStr, Field, model_validator
from pydantic.config import ConfigDict

from app.core.exceptions import unprocessable


class UserCreate(BaseModel):
    """创建用户入参。"""

    username: str = Field(min_length=3, max_length=64)
    phone: str = Field(min_length=6, max_length=20)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)
    nickname: str = Field(max_length=64)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _validate_phone(self) -> "UserCreate":
        """使用 phonenumbers 校验手机号，默认 CN 区号。

        兼容传入本地号（无国家码）与 E.164（+8613800000000）。
        """
        raw = self.phone or ""
        try:
            # 优先按本地区号 CN 解析；若已含国家码则也能识别
            parsed = phonenumbers.parse(raw, "CN")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError
        except Exception as e:
            raise unprocessable("手机号格式不正确") from e
        return self


class UserUpdate(BaseModel):
    """更新用户入参（部分字段可选）。"""

    version: int = Field(..., ge=0, description="乐观锁版本")
    username: str | None = Field(default=None, min_length=3, max_length=64)
    phone: str | None = Field(default=None, min_length=6, max_length=20)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=64)
    is_active: bool | None = None
    nickname: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=1000)
    avatar_url: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def _validate_phone(self) -> "UserUpdate":
        """使用 phonenumbers 校验可选手机号。"""
        if self.phone is None:
            return self
        try:
            parsed = phonenumbers.parse(self.phone, "CN")
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError
        except Exception as e:
            raise unprocessable("手机号格式不正确") from e
        return self


class UserQuery(BaseModel):
    """用户查询入参。"""

    keyword: str | None = Field(default=None, description="按用户名/手机号模糊搜索")


class UserOut(BaseModel):
    """用户出参模型。"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    version: int
    username: str
    phone: str
    email: EmailStr
    nickname: str
    bio: str | None = None
    avatar_url: str | None = None
    is_active: bool
    failed_attempts: int
    locked_until: datetime | None = None
    last_login_at: datetime | None = None
    created_at: datetime | None = None


class AdminChangePasswordIn(BaseModel):
    """管理员修改用户密码入参。"""

    new_password: str = Field(min_length=6, max_length=64)
    confirm_password: str = Field(min_length=6, max_length=64)

    @model_validator(mode="after")
    def _check_confirm(self) -> "AdminChangePasswordIn":
        """校验新密码与确认密码一致。"""
        if self.new_password != self.confirm_password:
            raise unprocessable("两次密码不一致")
        return self


class SelfChangePasswordIn(BaseModel):
    """用户自助修改密码入参。"""

    old_password: str = Field(min_length=6, max_length=64)
    new_password: str = Field(min_length=6, max_length=64)
    confirm_password: str = Field(min_length=6, max_length=64)

    @model_validator(mode="after")
    def _check_confirm(self) -> "SelfChangePasswordIn":
        """校验新密码与确认密码一致，且不等于旧密码。"""
        if self.new_password != self.confirm_password:
            raise unprocessable("两次密码不一致")
        if self.old_password == self.new_password:
            raise unprocessable("新密码不能与旧密码相同")
        return self


class UserIdsIn(BaseModel):
    """批量用户ID入参。"""

    ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> "UserIdsIn":
        if len(set(self.ids)) != len(self.ids):
            raise unprocessable("用户ID 列表存在重复")
        return self


class UserBindIn(BaseModel):
    """为用户绑定角色入参。"""

    user_id: int
    role_ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> "UserBindIn":
        if len(set(self.role_ids)) != len(self.role_ids):
            raise unprocessable("角色ID 列表存在重复")
        return self


class UsersBindIn(BaseModel):
    """为多个用户批量绑定角色入参。"""

    user_ids: list[int] = Field(min_length=1)
    role_ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> "UsersBindIn":
        if len(set(self.user_ids)) != len(self.user_ids):
            raise unprocessable("用户ID 列表存在重复")
        if len(set(self.role_ids)) != len(self.role_ids):
            raise unprocessable("角色ID 列表存在重复")
        return self
