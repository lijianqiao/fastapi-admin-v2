"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025/08/21 11:05:00
@Docs: DAO 基类，封装通用 CRUD、软删过滤、乐观锁与批量操作
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from tortoise import Model


class BaseDAO[ModelType: Model]:
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    # 统一只查询未软删
    def alive(self) -> Any:
        return self.model.filter(is_deleted=False)

    async def get_by_id(self, entity_id: int | str) -> ModelType | None:
        return await self.alive().filter(id=entity_id).first()

    async def get_many_by_ids(self, ids: Sequence[int | str]) -> list[ModelType]:
        return await self.alive().filter(id__in=list(ids)).all()

    async def exists(self, **filters: Any) -> bool:
        return await self.alive().filter(**filters).exists()

    async def count(self, **filters: Any) -> int:
        return await self.alive().filter(**filters).count()

    async def create(self, data: dict[str, Any]) -> ModelType:
        entity = await self.model.create(**data)
        return entity

    async def list_paginated(
        self,
        *,
        filters: dict[str, Any] | None = None,
        order_by: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[ModelType], int]:
        if page <= 0:
            page = 1
        if page_size <= 0:
            page_size = 20
        query = self.alive()
        if filters:
            query = query.filter(**filters)
        total = await query.count()
        if order_by:
            query = query.order_by(*order_by)
        else:
            query = query.order_by("-id")
        items = await query.offset((page - 1) * page_size).limit(page_size)
        return items, total

    async def update_with_version(self, entity_id: int | str, version: int, data: dict[str, Any]) -> int:
        # 乐观锁：id + version 条件更新
        update_data = {**data, "version": version + 1}
        updated = await self.alive().filter(id=entity_id, version=version).update(**update_data)
        return updated

    async def soft_delete(self, entity_id: int | str) -> int:
        updated = await self.model.filter(id=entity_id, is_deleted=False).update(is_deleted=True)
        return updated

    async def restore(self, entity_id: int | str) -> int:
        # 仅将软删记录恢复
        updated = await self.model.filter(id=entity_id, is_deleted=True).update(is_deleted=False)
        return updated

    async def hard_delete(self, entity_id: int | str) -> int:
        # 硬删除（谨慎使用）
        deleted = await self.model.filter(id=entity_id).delete()
        return deleted

    # 批量
    async def bulk_create(self, rows: Iterable[dict[str, Any]]) -> None:
        entities = [self.model(**row) for row in rows]
        await self.model.bulk_create(entities)

    async def bulk_update(self, rows: Iterable[dict[str, Any]], fields: Sequence[str]) -> int:
        # 需要 rows 中包含 id 与 version；逐条乐观锁更新以确保并发安全
        affected = 0
        for row in rows:
            entity_id = row.pop("id")
            version = row.pop("version")
            affected += await self.update_with_version(entity_id, version, row)
        return affected

    async def bulk_soft_delete(self, ids: Sequence[int | str]) -> int:
        return await self.model.filter(id__in=list(ids), is_deleted=False).update(is_deleted=True)

    async def bulk_restore(self, ids: Sequence[int | str]) -> int:
        return await self.model.filter(id__in=list(ids), is_deleted=True).update(is_deleted=False)

    async def bulk_upsert(self, rows: Iterable[dict[str, Any]]) -> int:
        # 简易 upsert：有 id+version 则乐观锁更新；否则创建
        affected = 0
        for row in rows:
            if "id" in row and "version" in row:
                entity_id = row["id"]
                version = row["version"]
                data = {k: v for k, v in row.items() if k not in {"id", "version"}}
                affected += await self.update_with_version(entity_id, version, data)
            else:
                await self.create(row)
                affected += 1
        return affected
