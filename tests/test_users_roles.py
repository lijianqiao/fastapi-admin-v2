"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_users_roles.py
@DateTime: 2025/08/26 15:30:00
@Docs: 用户角色绑定API测试
"""

from fastapi.testclient import TestClient


class TestUsersRoles:
    """用户角色绑定API测试"""

    def test_bind_roles_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试绑定角色成功"""
        # 先创建用户和角色
        import uuid

        unique_suffix = uuid.uuid4().hex[:8]
        # 生成纯数字的手机号后缀，避免UUID中的字母
        phone_suffix = str(abs(hash(unique_suffix)))[:8].zfill(8)

        user_data = {
            "username": f"binduser_{unique_suffix}",
            "phone": f"139{phone_suffix}",
            "email": f"bind_{unique_suffix}@example.com",
            "password": "test@123",
            "nickname": f"绑定用户_{unique_suffix}",
        }
        user_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        assert user_response.status_code == 200
        user_id = user_response.json()["data"]["id"]

        role_data = {
            "code": f"bind_role_{unique_suffix.lower()}",
            "name": f"绑定角色_{unique_suffix}",
            "description": "用于绑定测试的角色",
        }
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        assert role_response.status_code == 200
        role_id = role_response.json()["data"]["id"]

        # 绑定角色
        bind_data = {"user_id": user_id, "role_ids": [role_id]}
        response = client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_bind_roles_user_not_exist(self, client: TestClient, auth_headers: dict[str, str]):
        """测试绑定角色 - 用户不存在"""
        # 先创建一个角色
        import uuid

        unique_suffix = uuid.uuid4().hex[:8].lower()
        role_data = {
            "code": f"test_nonexist_user_{unique_suffix}",
            "name": f"测试角色_{unique_suffix}",
            "description": "用于测试的角色",
        }
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        assert role_response.status_code == 200, f"角色创建失败: {role_response.text}"
        role_id = role_response.json()["data"]["id"]

        # 使用不存在的用户ID
        bind_data = {"user_id": 999999, "role_ids": [role_id]}
        response = client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)
        # 用户不存在应该返回404
        assert response.status_code == 404

    def test_bind_roles_batch_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量绑定角色成功"""
        # 创建多个用户
        user_data_1 = {
            "username": "batchuser1",
            "phone": "13900000011",
            "email": "batch1@example.com",
            "password": "test@123",
            "nickname": "批量用户1",
        }
        user_data_2 = {
            "username": "batchuser2",
            "phone": "13900000012",
            "email": "batch2@example.com",
            "password": "test@123",
            "nickname": "批量用户2",
        }
        user1_response = client.post("/api/v1/users/", json=user_data_1, headers=auth_headers)
        user2_response = client.post("/api/v1/users/", json=user_data_2, headers=auth_headers)
        user1_id = user1_response.json()["data"]["id"]
        user2_id = user2_response.json()["data"]["id"]

        # 创建角色
        role_data = {"code": "batch_role", "name": "批量角色", "description": "用于批量绑定测试的角色"}
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = role_response.json()["data"]["id"]

        # 批量绑定角色（改用循环调用单个绑定端点）
        bind_data = {"user_id": None, "role_ids": [role_id]}
        for uid in [user1_id, user2_id]:
            bind_data["user_id"] = uid
            response = client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_unbind_roles_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试解绑角色成功"""
        # 先创建用户和角色并绑定
        user_data = {
            "username": "unbinduser",
            "phone": "13900000013",
            "email": "unbind@example.com",
            "password": "test@123",
            "nickname": "解绑用户",
        }
        user_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = user_response.json()["data"]["id"]

        role_data = {"code": "unbind_role", "name": "解绑角色", "description": "用于解绑测试的角色"}
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = role_response.json()["data"]["id"]

        # 先绑定
        bind_data = {"user_id": user_id, "role_ids": [role_id]}
        client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)

        # 解绑角色
        unbind_data = {"user_id": user_id, "role_ids": [role_id]}
        response = client.post("/api/v1/users/unbind-roles", json=unbind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_unbind_roles_batch_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量解绑角色成功"""
        # 创建多个用户
        user_data_1 = {
            "username": "unbatchuser1",
            "phone": "13900000014",
            "email": "unbatch1@example.com",
            "password": "test@123",
            "nickname": "批量解绑用户1",
        }
        user_data_2 = {
            "username": "unbatchuser2",
            "phone": "13900000015",
            "email": "unbatch2@example.com",
            "password": "test@123",
            "nickname": "批量解绑用户2",
        }
        user1_response = client.post("/api/v1/users/", json=user_data_1, headers=auth_headers)
        user2_response = client.post("/api/v1/users/", json=user_data_2, headers=auth_headers)
        user1_id = user1_response.json()["data"]["id"]
        user2_id = user2_response.json()["data"]["id"]

        # 创建角色
        role_data = {"code": "unbatch_role", "name": "批量解绑角色", "description": "用于批量解绑测试的角色"}
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = role_response.json()["data"]["id"]

        # 先绑定（改为单个绑定端点循环）
        bind_data = {"user_id": None, "role_ids": [role_id]}
        for uid in [user1_id, user2_id]:
            bind_data["user_id"] = uid
            client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)

        # 批量解绑（改用循环调用单个解绑端点）
        unbind_data = {"user_id": None, "role_ids": [role_id]}
        for uid in [user1_id, user2_id]:
            unbind_data["user_id"] = uid
            response = client.post("/api/v1/users/unbind-roles", json=unbind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_bind_roles_without_auth(self, client: TestClient):
        """测试未认证绑定角色"""
        bind_data = {"user_id": 1, "role_ids": [1]}
        response = client.post("/api/v1/users/bind-roles", json=bind_data)
        assert response.status_code == 401

    def test_unbind_roles_without_auth(self, client: TestClient):
        """测试未认证解绑角色"""
        unbind_data = {"user_id": 1, "role_ids": [1]}
        response = client.post("/api/v1/users/unbind-roles", json=unbind_data)
        assert response.status_code == 401
