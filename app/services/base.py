"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025/08/21 11:40:00
@Docs: 服务层基类
"""

from __future__ import annotations

from tortoise import Model

from app.dao.base import BaseDAO


class BaseService[ModelType: Model]:
    def __init__(self, dao: BaseDAO[ModelType]) -> None:
        self.dao = dao
