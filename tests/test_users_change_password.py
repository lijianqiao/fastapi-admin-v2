"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users_change_password.py
@DateTime: 2025/08/21 17:06:00
@Docs: 用户与管理员修改密码接口用例
"""

from __future__ import annotations

from fastapi.testclient import TestClient


def _login(client: TestClient, username: str = "admin", password: str = "admin@123") -> tuple[str, str]:
    r = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    j = r.json()
    return j.get("access_token", ""), j.get("refresh_token", "")


def _auth_headers(client: TestClient, username: str = "admin", password: str = "admin@123") -> dict[str, str]:
    at, _ = _login(client, username=username, password=password)
    return {"Authorization": f"Bearer {at}"}


def test_self_change_password_and_login_back(client: TestClient) -> None:
    # 先用管理员创建一个普通用户
    admin_headers = _auth_headers(client)
    cu = client.post(
        "/api/v1/users/",
        json={"username": "self_pwd_user", "phone": "13970000001", "password": "u@123456"},
        headers=admin_headers,
    )
    assert cu.status_code == 200
    # 该用户登录并自助修改密码
    user_headers = _auth_headers(client, username="self_pwd_user", password="u@123456")
    r = client.post(
        "/api/v1/users/me/password",
        json={"old_password": "u@123456", "new_password": "u@654321", "confirm_password": "u@654321"},
        headers=user_headers,
    )
    assert r.status_code == 200
    # 使用新密码能登录
    at, _ = _login(client, username="self_pwd_user", password="u@654321")
    assert at


def test_admin_change_user_password(client: TestClient) -> None:
    headers = _auth_headers(client)
    # 新建一个用户
    cu = client.post(
        "/api/v1/users/",
        json={"username": "pwd_user", "phone": "13999990001", "password": "u@123456"},
        headers=headers,
    )
    assert cu.status_code == 200
    uid = cu.json()["data"]["id"]
    # 管理员直接改密
    r = client.post(
        f"/api/v1/users/{uid}/password",
        json={"new_password": "u@654321", "confirm_password": "u@654321"},
        headers=headers,
    )
    assert r.status_code == 200
    # 新密码登录
    at, _ = _login(client, username="pwd_user", password="u@654321")
    assert at
