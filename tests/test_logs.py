"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_logs.py
@DateTime: 2025/08/21 15:34:00
@Docs: 审计日志 API 独立用例
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


def test_audit_log_list(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 触发一些写操作
    client.post("/api/v1/permissions/", json={"code": "perm:audit_x", "name": "审计X"}, headers=headers)

    # 查询日志（需要有 LOG_LIST 权限，admin/super_admin 已具备）
    r = client.get("/api/v1/logs/", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert "data" in j and "items" in j["data"]
