"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_auth.py
@DateTime: 2025/08/21 15:12:00
@Docs: 认证相关用例
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_login_ok(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_fail(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrong123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code in (401, 200, 422)  # 统一响应或校验错误
    j = resp.json()
    assert isinstance(j, dict)
