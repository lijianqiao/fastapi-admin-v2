"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:20:00
@Docs: 角色相关 Schemas
"""

from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RoleCreate(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    code: str = Field(min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=64)
    code: str | None = Field(default=None, min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class RoleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    description: str | None = None
    is_active: bool


class RoleBindIn(BaseModel):
    role_id: int
    target_ids: list[int] = Field(min_items=1)


class RoleIdsIn(BaseModel):
    ids: list[int] = Field(min_items=1)


class RolesBindIn(BaseModel):
    role_ids: list[int] = Field(min_items=1)
    permission_ids: list[int] = Field(min_items=1)
