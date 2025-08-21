"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_permissions.py
@DateTime: 2025/08/21 15:32:00
@Docs: 权限 API 独立用例
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


def test_permission_crud_and_disable(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 创建权限
    r = client.post("/api/v1/permissions/", json={"code": "perm:test_x", "name": "测试权限"}, headers=headers)
    assert r.status_code == 200
    pid = r.json()["data"]["id"]

    # 详情
    d = client.get(f"/api/v1/permissions/{pid}", headers=headers)
    assert d.status_code == 200

    # 列表
    ll = client.get("/api/v1/permissions/", headers=headers)
    assert ll.status_code == 200

    # 更新（乐观锁）
    ver = d.json()["data"]["version"]
    u = client.put(f"/api/v1/permissions/{pid}", params={"version": ver}, json={"name": "测试权限-新"}, headers=headers)
    assert u.status_code == 200

    # 禁用
    dis = client.post("/api/v1/permissions/disable", json={"ids": [pid]}, headers=headers)
    assert dis.status_code == 200
