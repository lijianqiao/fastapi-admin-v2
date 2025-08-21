"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles_disable.py
@DateTime: 2025/08/21 16:58:00
@Docs: 角色批量禁用接口用例
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


def test_roles_disable_batch(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 新建两个角色
    ids = []
    for i in range(2):
        r = client.post(
            "/api/v1/roles/",
            json={"code": f"r_dis_{i}", "name": f"RDIS_{i}"},
            headers=headers,
        )
        assert r.status_code == 200
        ids.append(r.json()["data"]["id"])

    dis = client.post("/api/v1/roles/disable", json={"ids": ids}, headers=headers)
    assert dis.status_code == 200
