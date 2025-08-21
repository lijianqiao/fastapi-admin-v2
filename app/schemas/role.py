"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:20:00
@Docs: 角色相关 Schemas
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RoleCreate(BaseModel):
    """创建角色入参。"""

    name: str = Field(min_length=2, max_length=64)
    code: str = Field(min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    """更新角色入参（部分字段可选）。"""

    name: str | None = Field(default=None, min_length=2, max_length=64)
    code: str | None = Field(default=None, min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class RoleOut(BaseModel):
    """角色出参模型。"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    version: int
    name: str
    code: str
    description: str | None = None
    is_active: bool
    created_at: datetime | None = None


class RoleBindIn(BaseModel):
    """为角色绑定权限入参。"""

    role_id: int
    target_ids: list[int] = Field(min_length=1)


class RoleIdsIn(BaseModel):
    """批量角色ID入参。"""

    ids: list[int] = Field(min_length=1)


class RolesBindIn(BaseModel):
    """为多个角色批量绑定权限入参。"""

    role_ids: list[int] = Field(min_length=1)
    permission_ids: list[int] = Field(min_length=1)
