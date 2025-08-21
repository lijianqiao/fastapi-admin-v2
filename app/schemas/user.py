"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:20:00
@Docs: 用户相关 Schemas
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator
from pydantic.config import ConfigDict

from app.core.exceptions import unprocessable


class UserCreate(BaseModel):
    """创建用户入参。"""

    username: str = Field(min_length=3, max_length=64)
    phone: str = Field(min_length=6, max_length=20, pattern=r"^\d{6,20}$")
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=64)


class UserUpdate(BaseModel):
    """更新用户入参（部分字段可选）。"""

    username: str | None = Field(default=None, min_length=3, max_length=64)
    phone: str | None = Field(default=None, min_length=6, max_length=20, pattern=r"^\d{6,20}$")
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6, max_length=64)
    is_active: bool | None = None


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
    email: EmailStr | None = None
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
    def _check_confirm(self) -> AdminChangePasswordIn:
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
    def _check_confirm(self) -> SelfChangePasswordIn:
        """校验新密码与确认密码一致，且不等于旧密码。"""
        if self.new_password != self.confirm_password:
            raise unprocessable("两次密码不一致")
        if self.old_password == self.new_password:
            raise unprocessable("新密码不能与旧密码相同")
        return self


class UserIdsIn(BaseModel):
    """批量用户ID入参。"""

    ids: list[int] = Field(min_length=1)


class UserBindIn(BaseModel):
    """为用户绑定角色入参。"""

    user_id: int
    role_ids: list[int] = Field(min_length=1)


class UsersBindIn(BaseModel):
    """为多个用户批量绑定角色入参。"""

    user_ids: list[int] = Field(min_length=1)
    role_ids: list[int] = Field(min_length=1)
