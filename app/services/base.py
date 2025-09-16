"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: base.py
@DateTime: 2025/08/21 11:40:00
@Docs: 服务层基类
"""

from tortoise.models import Model

from app.dao.base import BaseDAO


class BaseService[ModelType: Model]:
    """服务层基类。

    封装通用的 DAO 依赖注入，业务服务应继承该类并组合具体 DAO。

    Attributes:
        dao (BaseDAO[ModelType]): 具体实体的 DAO 实例。
    """

    def __init__(self, dao: BaseDAO[ModelType]) -> None:
        """初始化服务。

        Args:
            dao (BaseDAO[ModelType]): 具体实体的 DAO。
        """
        self.dao = dao
