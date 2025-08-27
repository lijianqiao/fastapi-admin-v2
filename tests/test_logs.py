"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_logs.py
@DateTime: 2025/08/26 15:30:00
@Docs: 审计日志API测试
"""

from fastapi.testclient import TestClient


class TestLogs:
    """审计日志API测试"""

    def test_list_logs_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试分页查询审计日志"""
        response = client.get("/api/v1/logs/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "page_size" in data["data"]

    def test_list_logs_with_filters(self, client: TestClient, auth_headers: dict[str, str]):
        """测试带过滤条件的审计日志查询"""
        # 先执行一些操作生成日志
        user_data = {
            "username": "loguser",
            "phone": "13900000030",
            "email": "loguser@example.com",
            "password": "test@123",
            "nickname": "日志用户",
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        # 查询日志，带过滤条件
        response = client.get("/api/v1/logs/?action=user:create&page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_list_logs_by_actor(self, client: TestClient, auth_headers: dict[str, str]):
        """测试按操作者查询审计日志"""
        # 获取当前用户ID（admin的ID通常是1）
        me_response = client.get("/api/v1/users/me", headers=auth_headers)
        actor_id = me_response.json()["data"]["id"]

        response = client.get(f"/api/v1/logs/?actor_id={actor_id}&page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_list_logs_by_trace_id(self, client: TestClient, auth_headers: dict[str, str]):
        """测试按追踪ID查询审计日志"""
        # 使用一个测试的trace_id
        response = client.get("/api/v1/logs/?trace_id=test-trace-123&page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_list_my_logs_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试查询我的操作记录"""
        # 先执行一些操作
        user_data = {
            "username": "myloguser",
            "phone": "13900000031",
            "email": "myloguser@example.com",
            "password": "test@123",
            "nickname": "我的日志用户",
        }
        client.post("/api/v1/users/", json=user_data, headers=auth_headers)

        # 查询我的操作记录
        response = client.get("/api/v1/logs/me?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]

    def test_list_logs_without_auth(self, client: TestClient):
        """测试未认证查询审计日志"""
        response = client.get("/api/v1/logs/")
        assert response.status_code == 401

    def test_list_my_logs_without_auth(self, client: TestClient):
        """测试未认证查询我的操作记录"""
        response = client.get("/api/v1/logs/me")
        assert response.status_code == 401

    def test_list_logs_pagination(self, client: TestClient, auth_headers: dict[str, str]):
        """测试审计日志分页参数"""
        # 测试第一页
        response = client.get("/api/v1/logs/?page=1&page_size=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 5

        # 测试第二页
        response = client.get("/api/v1/logs/?page=2&page_size=5", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 2

    def test_list_logs_invalid_page(self, client: TestClient, auth_headers: dict[str, str]):
        """测试无效的分页参数"""
        # 测试负数页码
        response = client.get("/api/v1/logs/?page=-1&page_size=10", headers=auth_headers)
        assert response.status_code == 422

        # 测试过大的page_size
        response = client.get("/api/v1/logs/?page=1&page_size=1000", headers=auth_headers)
        assert response.status_code == 422
