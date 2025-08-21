"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users.py
@DateTime: 2025/08/21 15:14:00
@Docs: 用户 API 用例（鉴权、CRUD、关系、异常）
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _login(client: TestClient) -> tuple[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin@123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    j = r.json()
    return j.get("access_token", ""), j.get("refresh_token", "")


def test_user_crud_and_bind(client: TestClient) -> None:
    at, _ = _login(client)
    headers = {"Authorization": f"Bearer {at}"}

    # 创建用户
    create = client.post(
        "/api/v1/users/",
        json={"username": "user001", "phone": "13900000001", "password": "pass@123"},
        headers=headers,
    )
    assert create.status_code == 200
    uid = create.json()["data"]["id"]

    # 查询详情
    detail = client.get(f"/api/v1/users/{uid}", headers=headers)
    assert detail.status_code == 200

    # 列表
    lst = client.get("/api/v1/users/", headers=headers)
    assert lst.status_code == 200

    # 乐观锁更新（先获取 version）
    version = detail.json()["data"].get("version", 0)
    upd = client.put(
        f"/api/v1/users/{uid}", params={"version": version}, json={"email": "u1@example.com"}, headers=headers
    )
    assert upd.status_code == 200

    # 绑定/解绑角色（使用已存在的 super_admin 角色做样例，id=1 可能变化，这里仅做流程验证）
    client.post("/api/v1/users/bind-roles", json={"user_id": uid, "role_ids": [1]}, headers=headers)
    client.post("/api/v1/users/unbind-roles", json={"user_id": uid, "role_ids": [1]}, headers=headers)
