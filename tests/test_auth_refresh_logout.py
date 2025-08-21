"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_auth_refresh_logout.py
@DateTime: 2025/08/21 16:55:00
@Docs: 认证刷新与注销接口用例
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _login_pair(client: TestClient) -> tuple[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    j = r.json()
    return j.get("access_token", ""), j.get("refresh_token", "")


def test_refresh_and_logout(client: TestClient) -> None:
    at, rt = _login_pair(client)

    # 刷新令牌
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": rt})
    assert r.status_code == 200
    j = r.json()
    assert j.get("access_token")
    assert j.get("refresh_token")

    # 注销（提升用户令牌版本）
    # 取 user_id=1 作为默认管理员（测试种子中创建）
    lg = client.post("/api/v1/auth/logout", params={"user_id": 1})
    assert lg.status_code == 200
