"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: conftest.py
@DateTime: 2025/08/21 15:10:00
@Docs: 测试环境配置（内存DB、TestClient、内置RBAC初始化）
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Generator

# 提前设置测试环境变量，确保导入应用前生效
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("DATABASE_URL", "sqlite://:memory:")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.main import app
from app.models import Permission, Role, RolePermission, User, UserRole
from app.utils.builtin_rbac import get_builtin_permissions, get_builtin_roles, get_role_permission_map
from app.utils.logger import setup_logger


@pytest.fixture(scope="session", autouse=True)
def _init_env() -> None:
    os.environ.setdefault("ENVIRONMENT", "testing")
    os.environ.setdefault("DATABASE_URL", "sqlite://:memory:")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
    setup_logger("testing")


async def _seed_builtin() -> None:
    # 权限
    code_to_id: dict[str, int] = {}
    for p in get_builtin_permissions():
        obj, _ = await Permission.get_or_create(
            code=str(p["code"]), defaults={"name": p["name"], "description": p["description"]}
        )
        code_to_id[obj.code] = int(obj.id)
    # 角色
    role_to_id: dict[str, int] = {}
    for r in get_builtin_roles():
        obj, _ = await Role.get_or_create(code=r["code"], defaults={"name": r["name"], "description": r["description"]})
        role_to_id[obj.code] = int(obj.id)
    # 绑定
    for role_code, perms in get_role_permission_map().items():
        rid = role_to_id.get(role_code)
        if not rid:
            continue
        for c in perms:
            pid = code_to_id.get(str(c))
            if pid:
                await RolePermission.get_or_create(role_id=rid, permission_id=pid)
    # 超级管理员
    u, _ = await User.get_or_create(
        username="admin",
        defaults={
            "phone": "13800000000",
            "email": "admin@example.com",
            "password_hash": hash_password("admin@123"),
        },
    )
    if role_to_id.get("super_admin"):
        await UserRole.get_or_create(user_id=int(u.id), role_id=role_to_id["super_admin"])


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        # 应用启动完成后再进行种子写入，避免连接尚未初始化
        asyncio.run(_seed_builtin())
        yield c
