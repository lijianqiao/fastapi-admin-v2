"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: user.py
@DateTime: 2025/08/21 11:20:00
@Docs: 用户相关 Schemas
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field
from pydantic.config import ConfigDict


class UserCreate(BaseModel):
    """创建用户入参。"""

    username: str = Field(min_length=3, max_length=64)
    phone: str = Field(min_length=6, max_length=20)
    email: EmailStr | None = None
    password: str = Field(min_length=6, max_length=64)


class UserUpdate(BaseModel):
    """更新用户入参（部分字段可选）。"""

    username: str | None = Field(default=None, min_length=3, max_length=64)
    phone: str | None = Field(default=None, min_length=6, max_length=20)
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
    username: str
    phone: str
    email: EmailStr | None = None
    is_active: bool
    failed_attempts: int
    locked_until: str | None = None
    last_login_at: str | None = None


class UserIdsIn(BaseModel):
    """批量用户ID入参。"""

    ids: list[int] = Field(min_items=1)


class UserBindIn(BaseModel):
    """为用户绑定角色入参。"""

    user_id: int
    role_ids: list[int] = Field(min_items=1)


class UsersBindIn(BaseModel):
    """为多个用户批量绑定角色入参。"""

    user_ids: list[int] = Field(min_items=1)
    role_ids: list[int] = Field(min_items=1)
