"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_permissions_disable.py
@DateTime: 2025/08/21 16:49:00
@Docs: 权限批量禁用接口用例
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


def test_permissions_disable_batch(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 新建两个权限
    ids = []
    for i in range(2):
        r = client.post(
            "/api/v1/permissions/",
            json={"code": f"perm:dis_{i}", "name": f"DIS_{i}"},
            headers=headers,
        )
        assert r.status_code == 200
        ids.append(r.json()["data"]["id"])

    dis = client.post("/api/v1/permissions/disable", json={"ids": ids}, headers=headers)
    assert dis.status_code == 200
