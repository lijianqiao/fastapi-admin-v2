"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: permission.py
@DateTime: 2025/08/21 11:20:00
@Docs: 权限相关 Schemas
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict


class PermissionCreate(BaseModel):
    """创建权限入参。"""

    code: str = Field(min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$")
    name: str = Field(min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)


class PermissionUpdate(BaseModel):
    """更新权限入参（部分字段可选）。"""

    code: str | None = Field(default=None, min_length=2, max_length=64, pattern=r"^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$")
    name: str | None = Field(default=None, min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class PermissionOut(BaseModel):
    """权限出参模型。"""

    model_config = ConfigDict(from_attributes=True)
    id: int
    version: int
    code: str
    name: str
    description: str | None = None
    is_active: bool
    created_at: datetime | None = None


class PermissionIdsIn(BaseModel):
    """批量权限ID入参。"""

    ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> PermissionIdsIn:
        from app.core.exceptions import unprocessable

        if len(set(self.ids)) != len(self.ids):
            raise unprocessable("权限ID 列表存在重复")
        return self
