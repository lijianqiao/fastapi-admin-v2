"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: system_config.py
@DateTime: 2025/08/27 15:22:00
@Docs: 系统配置 DAO
"""

from datetime import UTC, datetime

from app.core.exceptions import conflict
from app.dao.base import BaseDAO
from app.models.system_config import SystemConfig


class SystemConfigDAO(BaseDAO[SystemConfig]):
    def __init__(self) -> None:
        super().__init__(SystemConfig)

    async def get_singleton(self) -> SystemConfig:
        """获取单例配置记录，若不存在则创建默认记录。

        Returns:
            SystemConfig: 单例配置记录
        """
        inst = await self.model.filter(id=1).first()
        if inst:
            return inst
        # 若不存在则创建默认记录
        now = datetime.now(tz=UTC)
        return await self.model.create(id=1, created_at=now, updated_at=now)

    async def update_partial(self, data: dict[str, object]) -> SystemConfig:
        """更新部分配置（带乐观锁，并刷新更新时间）。

        - 使用当前版本号执行 `WHERE id=? AND version=?` 更新；
        - 更新成功自动将 version+1，且写入 updated_at；
        - 如因并发导致版本不匹配，抛出 409 冲突。

        Args:
            data (dict[str, object]): 更新数据

        Returns:
            SystemConfig: 更新后的配置
        """
        inst = await self.get_singleton()
        # 使用基类的乐观锁更新，内部会设置 updated_at 与自增 version
        affected = await self.update_with_version(inst.id, inst.version, data)
        if affected == 0:
            raise conflict("配置已被其他人修改，请刷新后重试")
        return await self.model.get(id=inst.id)


__all__ = ["SystemConfigDAO"]
