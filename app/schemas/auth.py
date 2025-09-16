"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: auth.py
@DateTime: 2025/08/21 11:20:00
@Docs: 认证相关 Schemas（登录、刷新）
"""

from typing import TypedDict

from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    """登录入参。"""

    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=64)


class RefreshIn(BaseModel):
    """刷新令牌入参。"""

    refresh_token: str


class TokenOut(BaseModel):
    """令牌出参。"""

    access_token: str
    token_type: str = Field(default="bearer")
    refresh_token: str | None = None


class TokenPair(TypedDict):
    """令牌对
    Args:
        access_token (str): 访问令牌
        refresh_token (str): 刷新令牌
        token_type (str): 令牌类型
    """

    access_token: str
    refresh_token: str
    token_type: str
