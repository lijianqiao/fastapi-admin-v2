"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles.py
@DateTime: 2025/08/21 15:30:00
@Docs: 角色 API 独立用例
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _login(client: TestClient) -> str:
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return r.json().get("access_token", "")


def test_role_crud_and_bind(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 创建角色
    r = client.post("/api/v1/roles/", json={"code": "r1", "name": "R1"}, headers=headers)
    assert r.status_code == 200
    rid = r.json()["data"]["id"]

    # 详情
    d = client.get(f"/api/v1/roles/{rid}", headers=headers)
    assert d.status_code == 200

    # 列表
    l = client.get("/api/v1/roles/", headers=headers)
    assert l.status_code == 200

    # 更新（乐观锁）
    ver = d.json()["data"]["version"]
    u = client.put(f"/api/v1/roles/{rid}", params={"version": ver}, json={"name": "R1-new"}, headers=headers)
    assert u.status_code == 200

    # 绑定/解绑权限（取已存在的权限 code 列表前两项，保底为空数组不报错）
    perms_list = client.get("/api/v1/permissions/", headers=headers).json()["data"]["items"]
    perm_ids = [p["id"] for p in perms_list[:2]] if perms_list else []
    client.post("/api/v1/roles/bind-permissions", json={"role_id": rid, "target_ids": perm_ids}, headers=headers)
    client.post("/api/v1/roles/unbind-permissions", json={"role_id": rid, "target_ids": perm_ids}, headers=headers)
