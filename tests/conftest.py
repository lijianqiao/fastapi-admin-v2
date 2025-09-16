"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: conftest.py
@DateTime: 2025/08/26 15:30:00
@Docs: 测试环境配置（内存DB、TestClient、内置RBAC初始化）
"""

import asyncio
import os
import uuid
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
        code_val = p["code"].value if hasattr(p["code"], "value") else p["code"]
        obj, _ = await Permission.get_or_create(
            code=code_val, defaults={"name": p["name"], "description": p["description"]}
        )
        code_to_id[str(obj.code)] = int(obj.id)
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
            code_key = c.value if hasattr(c, "value") else c
            pid = code_to_id.get(str(code_key))
            if pid:
                await RolePermission.get_or_create(role_id=rid, permission_id=pid)
    # 超级管理员
    u, _ = await User.get_or_create(
        username="admin",
        defaults={
            "phone": "13800000000",
            "email": "admin@example.com",
            "nickname": "系统管理员",
            "password_hash": hash_password("admin@123"),
        },
    )
    # 确保管理员处于可登录状态（重置锁定与失败计数，并统一密码）
    await User.filter(id=u.id).update(
        password_hash=hash_password("admin@123"), failed_attempts=0, locked_until=None, is_active=True
    )
    if role_to_id.get("super_admin"):
        await UserRole.get_or_create(user_id=int(u.id), role_id=role_to_id["super_admin"])


@pytest.fixture(scope="session")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        # 应用启动完成后再进行种子写入，避免连接尚未初始化
        asyncio.run(_seed_builtin())
        yield c


@pytest.fixture
def admin_token(client: TestClient) -> str:
    """获取管理员token"""
    # 先尝试用默认口令登录
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin@123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]

    # 若失败，可能上次用例修改了口令：尝试使用测试用例中常用的新口令登录并改回默认
    fallback = client.post("/api/v1/auth/login", data={"username": "admin", "password": "new_password@123"})
    if fallback.status_code == 200:
        tmp_token = fallback.json()["access_token"]
        headers = {"Authorization": f"Bearer {tmp_token}"}
        # 改回默认口令
        client.post(
            "/api/v1/users/me/password",
            json={
                "old_password": "new_password@123",
                "new_password": "admin@123",
                "confirm_password": "admin@123",
            },
            headers=headers,
        )
        # 使用默认口令重新登录
        resp2 = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin@123"})
        assert resp2.status_code == 200
        return resp2.json()["access_token"]

    # 如果仍失败，直接抛出以便定位具体响应
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict[str, str]:
    """认证头部"""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def test_user_data() -> dict:
    """测试用户数据"""
    unique_suffix = uuid.uuid4().hex[:8]
    # 生成纯数字的手机号后缀，避免UUID中的字母
    phone_suffix = str(abs(hash(unique_suffix)))[:8].zfill(8)
    return {
        "username": f"testuser_{unique_suffix}",
        "phone": f"139{phone_suffix}",
        "email": f"testuser_{unique_suffix}@example.com",
        "password": "test@123",
        "nickname": f"测试用户_{unique_suffix}",
    }


@pytest.fixture
def test_role_data() -> dict:
    """测试角色数据"""
    unique_suffix = uuid.uuid4().hex[:8]
    return {"code": f"test_role_{unique_suffix}", "name": f"测试角色_{unique_suffix}", "description": "用于测试的角色"}


@pytest.fixture
def test_permission_data() -> dict:
    """测试权限数据"""
    unique_suffix = uuid.uuid4().hex[:8]
    return {
        "code": f"test:action_{unique_suffix}",
        "name": f"测试权限_{unique_suffix}",
        "description": "用于测试的权限",
    }
