"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025/08/21 11:05:00
@Docs: DAO 基类，封装通用 CRUD、软删过滤、乐观锁与批量操作
"""

from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from typing import Any

from tortoise.models import Model


class BaseDAO[ModelType: Model]:
    """通用 DAO 基类，封装标准 CRUD、分页、软删与乐观锁操作。

    Args:
        model (type[ModelType]): Tortoise 模型类型。

    Notes:
        - 所有读取默认只返回未软删记录（`is_deleted=False`）。
        - 更新建议通过 `update_with_version` 保证乐观锁一致性。
    """

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    # 统一只查询未软删
    def alive(self) -> Any:
        """仅查询未软删记录。

        Returns:
            Any: 可继续链式调用的查询对象。
        """
        return self.model.filter(is_deleted=False)

    async def get_by_id(self, entity_id: int | str) -> ModelType | None:
        """按主键获取实体（未软删）。

        Args:
            entity_id (int | str): 主键ID。

        Returns:
            ModelType | None: 实体或 None。
        """
        return await self.alive().filter(id=entity_id).first()

    async def get_many_by_ids(self, ids: Sequence[int | str]) -> list[ModelType]:
        """批量按主键获取实体列表（未软删）。

        Args:
            ids (Sequence[int | str]): 主键ID列表。

        Returns:
            list[ModelType]: 实体列表。
        """
        return await self.alive().filter(id__in=list(ids)).all()

    async def exists(self, **filters: Any) -> bool:
        """判断是否存在满足条件的记录（未软删）。

        Returns:
            bool: 是否存在。
        """
        return await self.alive().filter(**filters).exists()

    async def count(self, **filters: Any) -> int:
        """统计满足条件的记录数（未软删）。

        Returns:
            int: 计数。
        """
        return await self.alive().filter(**filters).count()

    async def create(self, data: dict[str, Any]) -> ModelType:
        """创建实体。

        Args:
            data (dict[str, Any]): 字段字典。

        Returns:
            ModelType: 新建的实体。
        """
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
        """分页查询（未软删）。

        Args:
            filters (dict[str, Any] | None): 过滤条件。
            order_by (list[str] | None): 排序字段列表（如 ["-id"]）。
            page (int): 页码，从 1 开始。
            page_size (int): 每页数量。

        Returns:
            tuple[list[ModelType], int]: (items, total) 实体列表与总数。
        """
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
        """带乐观锁的更新：`WHERE id=? AND version=?`。

        Args:
            entity_id (int | str): 主键ID。
            version (int): 当前版本号。
            data (dict[str, Any]): 待更新字段（不含 version）。

        Returns:
            int: 受影响行数，0 表示冲突或不存在。
        """
        now = datetime.now(tz=UTC)
        update_data = {**data, "version": version + 1, "updated_at": now}
        updated = await self.alive().filter(id=entity_id, version=version).update(**update_data)
        return updated

    async def soft_delete(self, entity_id: int | str) -> int:
        """软删除记录。

        Returns:
            int: 受影响行数。
        """
        now = datetime.now(tz=UTC)
        updated = await self.model.filter(id=entity_id, is_deleted=False).update(
            is_deleted=True, deleted_at=now, updated_at=now
        )
        return updated

    async def restore(self, entity_id: int | str) -> int:
        """恢复被软删记录。

        Returns:
            int: 受影响行数。
        """
        now = datetime.now(tz=UTC)
        updated = await self.model.filter(id=entity_id, is_deleted=True).update(
            is_deleted=False, deleted_at=None, updated_at=now
        )
        return updated

    async def hard_delete(self, entity_id: int | str) -> int:
        """硬删除（谨慎使用）。

        Returns:
            int: 受影响行数。
        """
        deleted = await self.model.filter(id=entity_id).delete()
        return deleted

    # 批量
    async def bulk_create(self, rows: Iterable[dict[str, Any]]) -> None:
        """批量创建。

        Args:
            rows (Iterable[dict[str, Any]]): 字段字典迭代器。
        """
        entities = [self.model(**row) for row in rows]
        await self.model.bulk_create(entities)

    async def bulk_update(self, rows: Iterable[dict[str, Any]], fields: Sequence[str]) -> int:
        """批量更新（逐条乐观锁）。

        Args:
            rows (Iterable[dict[str, Any]]): 每项需包含 `id` 与 `version`。
            fields (Sequence[str]): 更新的字段列表（仅用于自描述，无强校验）。

        Returns:
            int: 累计受影响行数。
        """
        affected = 0
        now = datetime.now(tz=UTC)
        for row in rows:
            entity_id = row.pop("id")
            version = row.pop("version")
            row["updated_at"] = now
            affected += await self.update_with_version(entity_id, version, row)
        return affected

    async def bulk_soft_delete(self, ids: Sequence[int | str]) -> int:
        """批量软删除。

        Returns:
            int: 受影响行数。
        """
        now = datetime.now(tz=UTC)
        return await self.model.filter(id__in=list(ids), is_deleted=False).update(
            is_deleted=True, deleted_at=now, updated_at=now
        )

    async def bulk_restore(self, ids: Sequence[int | str]) -> int:
        """批量恢复软删记录。

        Returns:
            int: 受影响行数。
        """
        now = datetime.now(tz=UTC)
        return await self.model.filter(id__in=list(ids), is_deleted=True).update(
            is_deleted=False, deleted_at=None, updated_at=now
        )

    async def bulk_upsert(self, rows: Iterable[dict[str, Any]]) -> int:
        """批量 upsert（有 `id+version` 则乐观锁更新，否则创建）。

        Args:
            rows (Iterable[dict[str, Any]]): 字段字典迭代器。

        Returns:
            int: 总影响条数（创建计 1，更新计影响行数）。
        """
        affected = 0
        now = datetime.now(tz=UTC)
        for row in rows:
            if "id" in row and "version" in row:
                entity_id = row["id"]
                version = row["version"]
                data = {k: v for k, v in row.items() if k not in {"id", "version"}}
                data["updated_at"] = now
                affected += await self.update_with_version(entity_id, version, data)
            else:
                await self.create(row)
                affected += 1
        return affected
