"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users_me.py
@DateTime: 2025/08/21 17:05:00
@Docs: 当前用户自查接口用例
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _login(client: TestClient, username: str = "admin", password: str = "admin@123") -> str:
    r = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return r.json().get("access_token", "")


def test_get_me(client: TestClient) -> None:
    # 使用管理员登录
    at = _login(client, username="admin", password="admin@123")
    headers = {"Authorization": f"Bearer {at}"}
    r = client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert j.get("data", {}).get("username") == "admin"
