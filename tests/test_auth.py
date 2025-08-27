"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_auth.py
@DateTime: 2025/08/26 15:30:00
@Docs: 认证相关API测试
"""

from fastapi.testclient import TestClient


class TestAuth:
    """认证API测试"""

    def test_login_success(self, client: TestClient):
        """测试登录成功"""
        response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin@123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_username(self, client: TestClient):
        """测试用户名错误"""
        response = client.post("/api/v1/auth/login", data={"username": "invalid_user", "password": "admin@123"})
        assert response.status_code == 401

    def test_login_invalid_password(self, client: TestClient):
        """测试密码错误"""
        response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "wrong_password"})
        assert response.status_code == 401

    def test_login_missing_fields(self, client: TestClient):
        """测试缺少必填字段"""
        response = client.post("/api/v1/auth/login", data={"username": "admin"})
        assert response.status_code == 422

    def test_refresh_token_success(self, client: TestClient):
        """测试刷新令牌成功"""
        # 先登录获取refresh_token
        login_response = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin@123"})
        refresh_token = login_response.json()["refresh_token"]

        # 刷新令牌
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """测试无效的刷新令牌"""
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "invalid_token"})
        assert response.status_code == 401

    def test_logout_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试注销成功"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["message"] == "success"
        assert "注销成功" in str(data["data"])

    def test_logout_without_auth(self, client: TestClient):
        """测试未认证的注销请求"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401
