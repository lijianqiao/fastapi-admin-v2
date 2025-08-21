"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles_batch.py
@DateTime: 2025/08/21 16:47:00
@Docs: 角色批量权限绑定/解绑接口用例
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


def _ensure_two_permissions(client: TestClient, headers: dict[str, str]) -> list[int]:
    ids: list[int] = []
    for code in ("perm:rbac_a", "perm:rbac_b"):
        r = client.post("/api/v1/permissions/", json={"code": code, "name": code}, headers=headers)
        if r.status_code == 200:
            ids.append(r.json()["data"]["id"])
    return ids


def test_roles_bind_unbind_batch(client: TestClient) -> None:
    at = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 新建角色
    r = client.post("/api/v1/roles/", json={"code": "r_batch", "name": "RBATCH"}, headers=headers)
    assert r.status_code == 200
    rid = r.json()["data"]["id"]

    # 确保存在两个权限
    pids = _ensure_two_permissions(client, headers)

    # 批量绑定
    b = client.post(
        "/api/v1/roles/bind-permissions/batch",
        json={"role_ids": [rid], "permission_ids": pids},
        headers=headers,
    )
    assert b.status_code == 200

    # 批量解绑
    ub = client.post(
        "/api/v1/roles/unbind-permissions/batch",
        json={"role_ids": [rid], "permission_ids": pids},
        headers=headers,
    )
    assert ub.status_code == 200
