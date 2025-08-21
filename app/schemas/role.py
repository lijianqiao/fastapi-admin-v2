"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: role.py
@DateTime: 2025/08/21 11:20:00
@Docs: 角色相关 Schemas
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator
from pydantic.config import ConfigDict


class RoleCreate(BaseModel):
    """创建角色入参。"""

    name: str = Field(min_length=2, max_length=64)
    code: str = Field(min_length=2, max_length=64, pattern=r"^[a-z0-9_\-]{2,64}$")
    description: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    """更新角色入参（部分字段可选）。"""

    name: str | None = Field(default=None, min_length=2, max_length=64)
    code: str | None = Field(default=None, min_length=2, max_length=64, pattern=r"^[a-z0-9_\-]{2,64}$")
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

    @model_validator(mode="after")
    def _no_dup(self) -> RoleBindIn:
        if len(set(self.target_ids)) != len(self.target_ids):
            from app.core.exceptions import unprocessable

            raise unprocessable("权限ID 列表存在重复")
        return self


class RoleIdsIn(BaseModel):
    """批量角色ID入参。"""

    ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> RoleIdsIn:
        if len(set(self.ids)) != len(self.ids):
            from app.core.exceptions import unprocessable

            raise unprocessable("角色ID 列表存在重复")
        return self


class RolesBindIn(BaseModel):
    """为多个角色批量绑定权限入参。"""

    role_ids: list[int] = Field(min_length=1)
    permission_ids: list[int] = Field(min_length=1)

    @model_validator(mode="after")
    def _no_dup(self) -> RolesBindIn:
        from app.core.exceptions import unprocessable

        if len(set(self.role_ids)) != len(self.role_ids):
            raise unprocessable("角色ID 列表存在重复")
        if len(set(self.permission_ids)) != len(self.permission_ids):
            raise unprocessable("权限ID 列表存在重复")
        return self
