"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users_batch.py
@DateTime: 2025/08/21 16:45:00
@Docs: 用户批量接口与关系批量接口用例
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


def _get_any_role_id(client: TestClient, headers: dict[str, str]) -> int:
    r = client.get("/api/v1/roles/", headers=headers)
    items = r.json()["data"]["items"]
    return items[0]["id"] if items else 0


def test_users_batch_disable_and_bind(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 创建两个用户
    ids: list[int] = []
    for i in range(2):
        r = client.post(
            "/api/v1/users/",
            json={"username": f"ub{i:03d}", "phone": f"1390000001{i}", "password": "pass@123"},
            headers=headers,
        )
        assert r.status_code == 200
        ids.append(r.json()["data"]["id"])

    # 批量禁用
    dis = client.post("/api/v1/users/disable", json={"ids": ids}, headers=headers)
    assert dis.status_code == 200

    # 批量绑定/解绑角色
    role_id = _get_any_role_id(client, headers)
    b = client.post(
        "/api/v1/users/bind-roles/batch",
        json={"user_ids": ids, "role_ids": [role_id] if role_id else []},
        headers=headers,
    )
    assert b.status_code == 200
    ub = client.post(
        "/api/v1/users/unbind-roles/batch",
        json={"user_ids": ids, "role_ids": [role_id] if role_id else []},
        headers=headers,
    )
    assert ub.status_code == 200
