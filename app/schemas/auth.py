"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 11:20:00
@Docs: 认证相关 Schemas（登录、刷新）
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class RefreshIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")
    refresh_token: str | None = None
