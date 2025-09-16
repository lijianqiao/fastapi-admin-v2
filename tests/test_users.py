"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users.py
@DateTime: 2025/08/26 15:30:00
@Docs: 用户管理API测试
"""

from fastapi.testclient import TestClient


class TestUsers:
    """用户管理API测试"""

    def test_get_current_user(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取当前用户信息"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == "admin"

    def test_get_current_user_without_auth(self, client: TestClient):
        """测试未认证获取当前用户"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_self_change_password_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试自助修改密码成功"""
        password_data = {
            "old_password": "admin@123",
            "new_password": "new_password@123",
            "confirm_password": "new_password@123",
        }
        response = client.post("/api/v1/users/me/password", json=password_data, headers=auth_headers)
        assert response.status_code == 200

        # 改回原密码
        password_data_back = {
            "old_password": "new_password@123",
            "new_password": "admin@123",
            "confirm_password": "admin@123",
        }
        client.post("/api/v1/users/me/password", json=password_data_back, headers=auth_headers)

    def test_self_change_password_wrong_old_password(self, client: TestClient, auth_headers: dict[str, str]):
        """测试自助修改密码 - 旧密码错误"""
        password_data = {
            "old_password": "wrong_old_password",
            "new_password": "new_password@123",
            "confirm_password": "new_password@123",
        }
        response = client.post("/api/v1/users/me/password", json=password_data, headers=auth_headers)
        assert response.status_code == 409

    def test_self_change_password_mismatch(self, client: TestClient, auth_headers: dict[str, str]):
        """测试自助修改密码 - 新密码不匹配"""
        password_data = {
            "old_password": "admin@123",
            "new_password": "new_password@123",
            "confirm_password": "different_password@123",
        }
        response = client.post("/api/v1/users/me/password", json=password_data, headers=auth_headers)
        assert response.status_code in [409, 422]  # 密码不匹配可能返回422(验证错误)或409(业务冲突)

    def test_create_user_success(self, client: TestClient, auth_headers: dict[str, str], test_user_data: dict):
        """测试创建用户成功"""
        response = client.post("/api/v1/users/", json=test_user_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == test_user_data["username"]
        # 不返回值，避免 pytest 警告

    def test_create_user_duplicate_username(self, client: TestClient, auth_headers: dict[str, str]):
        """测试创建用户 - 用户名重复"""
        user_data = {
            "username": "admin",  # 已存在的用户名
            "phone": "13900000002",
            "email": "duplicate@example.com",
            "password": "test@123",
            "nickname": "重复用户",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert response.status_code == 409

    def test_create_user_without_auth(self, client: TestClient, test_user_data: dict):
        """测试未认证创建用户"""
        response = client.post("/api/v1/users/", json=test_user_data)
        assert response.status_code == 401

    def test_get_user_detail(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取用户详情"""
        # 先创建一个用户
        user_data = {
            "username": "detailuser",
            "phone": "13900000003",
            "email": "detail@example.com",
            "password": "test@123",
            "nickname": "详情用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 获取用户详情
        response = client.get(f"/api/v1/users/{user_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["username"] == user_data["username"]

    def test_get_user_detail_not_found(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取不存在的用户详情"""
        response = client.get("/api/v1/users/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_list_users(self, client: TestClient, auth_headers: dict[str, str]):
        """测试分页查询用户列表"""
        response = client.get("/api/v1/users/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "page_size" in data["data"]

    def test_list_users_with_keyword(self, client: TestClient, auth_headers: dict[str, str]):
        """测试关键字搜索用户"""
        response = client.get("/api/v1/users/?keyword=admin&page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200

    def test_update_user_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新用户成功"""
        # 先创建一个用户
        user_data = {
            "username": "updateuser",
            "phone": "13900000004",
            "email": "update@example.com",
            "password": "test@123",
            "nickname": "更新用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 更新用户
        update_data = {"version": 0, "nickname": "已更新用户"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 200

    def test_update_user_version_conflict(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新用户 - 版本冲突"""
        # 先创建一个用户
        user_data = {
            "username": "conflictuser",
            "phone": "13900000005",
            "email": "conflict@example.com",
            "password": "test@123",
            "nickname": "冲突用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 使用错误的版本号更新
        update_data = {"version": 999, "nickname": "冲突更新"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data, headers=auth_headers)
        assert response.status_code == 409

    def test_disable_users(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量禁用用户"""
        # 先创建一个用户
        user_data = {
            "username": "disableuser",
            "phone": "13900000006",
            "email": "disable@example.com",
            "password": "test@123",
            "nickname": "禁用用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 禁用用户
        response = client.post("/api/v1/users/disable", json={"ids": [user_id]}, headers=auth_headers)
        assert response.status_code == 200

    def test_admin_change_password(self, client: TestClient, auth_headers: dict[str, str]):
        """测试管理员修改用户密码"""
        # 先创建一个用户
        user_data = {
            "username": "pwduser",
            "phone": "13900000007",
            "email": "pwd@example.com",
            "password": "test@123",
            "nickname": "密码用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 管理员修改密码
        password_data = {"new_password": "new_admin_password@123", "confirm_password": "new_admin_password@123"}
        response = client.post(f"/api/v1/users/{user_id}/password", json=password_data, headers=auth_headers)
        assert response.status_code == 200

    def test_unlock_user(self, client: TestClient, auth_headers: dict[str, str]):
        """测试解锁用户"""
        # 先创建一个用户
        user_data = {
            "username": "lockuser",
            "phone": "13900000008",
            "email": "lock@example.com",
            "password": "test@123",
            "nickname": "锁定用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 解锁用户
        response = client.post(f"/api/v1/users/{user_id}/unlock", headers=auth_headers)
        assert response.status_code == 200
