"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_regressions.py
@DateTime: 2025/08/27 20:10:00
@Docs: 回归用例：权限缓存空标记与软删恢复一致性
"""

import pytest
from fastapi.testclient import TestClient

from app.dao.permission import PermissionDAO


def test_permission_cache_empty_sentinel_no_type_conflict(client: TestClient, admin_token: str):
    """当用户无任何权限时，通过 HTTP 触发权限校验应返回 403；绑定角色+权限并触发版本提升后应返回 200。"""
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 1) 管理员创建一个普通用户（无任何角色/权限）
    user_body = {
        "username": "perm_empty_u",
        "phone": "13910000001",
        "email": "perm_empty_u@example.com",
        "password": "x123456",
        "nickname": "p0",
    }
    r = client.post("/api/v1/users/", headers=admin_headers, json=user_body)
    assert r.status_code == 200, r.text
    new_user = r.json()["data"]
    uid = int(new_user["id"])

    # 2) 新用户登录获取 token
    r = client.post("/api/v1/auth/login", data={"username": user_body["username"], "password": user_body["password"]})
    assert r.status_code == 200, r.text
    user_token = r.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 3) 访问需要 user:list 的接口，应 403（无权限时应建立空标记但不产生类型冲突）
    r = client.get("/api/v1/users/", headers=user_headers)
    assert r.status_code == 403

    # 4) 管理员创建一个临时角色，并为其绑定 user:list 权限
    r = client.post(
        "/api/v1/roles/",
        headers=admin_headers,
        json={"name": "回归角色", "code": "reg_role_empty", "description": "reg"},
    )
    assert r.status_code == 200, r.text
    role_id = int(r.json()["data"]["id"])

    # 找到内置的 user:list 权限ID
    r = client.get("/api/v1/permissions/", headers=admin_headers, params={"page": 1, "page_size": 200})
    assert r.status_code == 200, r.text
    perms = r.json()["data"]["items"]
    pid = next(int(p["id"]) for p in perms if p["code"] == "user:list")

    # 为角色绑定权限（该接口会 bump 版本，进而失效旧缓存）
    r = client.post(
        "/api/v1/roles/bind-permissions",
        headers=admin_headers,
        json={"role_id": role_id, "target_ids": [pid]},
    )
    assert r.status_code == 200, r.text

    # 5) 将角色绑定给用户（接口内部也会触发版本提升）
    r = client.post(
        "/api/v1/users/bind-roles",
        headers=admin_headers,
        json={"user_id": uid, "role_ids": [role_id]},
    )
    assert r.status_code == 200, r.text

    # 6) 新用户再次访问需要 user:list 的接口，应 200
    r = client.get("/api/v1/users/", headers=user_headers)
    assert r.status_code == 200, r.text


@pytest.mark.asyncio
async def test_soft_delete_and_restore_deleted_at_consistency(client: TestClient):
    """软删应写入 deleted_at，恢复应将 deleted_at 置 None，批量操作也一致。"""
    perm_dao = PermissionDAO()
    # 创建一条权限
    p = await perm_dao.create({"code": "tmp:del_restore", "name": "tmp", "description": "t"})

    # 软删
    await perm_dao.delete_permission(int(p.id))  # type: ignore[arg-type]
    row = await perm_dao.model.filter(id=p.id).first()
    assert row is not None
    assert getattr(row, "is_deleted", False) is True
    assert getattr(row, "deleted_at", None) is not None

    # 恢复
    await perm_dao.restore(int(p.id))  # type: ignore[arg-type]
    row2 = await perm_dao.model.filter(id=p.id).first()
    assert row2 is not None
    assert getattr(row2, "is_deleted", True) is False
    assert getattr(row2, "deleted_at", "X") is None
