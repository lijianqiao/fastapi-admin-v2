"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles_users_list.py
@DateTime: 2025/08/21 17:08:00
@Docs: 查看角色下的用户接口用例
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


def test_list_users_of_role(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}
    # 任取一个角色（如种子 super_admin），读取其下用户
    r = client.get("/api/v1/roles/", headers=headers)
    assert r.status_code == 200
    items = r.json()["data"]["items"]
    if not items:
        return
    rid = items[0]["id"]
    u = client.get(f"/api/v1/roles/{rid}/users", headers=headers)
    assert u.status_code == 200
    ju = u.json()
    assert "data" in ju and "items" in ju["data"]
