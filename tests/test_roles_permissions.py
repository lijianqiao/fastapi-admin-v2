"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles_permissions.py
@DateTime: 2025/08/26 15:30:00
@Docs: 角色权限绑定API测试
"""

from fastapi.testclient import TestClient


class TestRolesPermissions:
    """角色权限绑定API测试"""

    def test_bind_permissions_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试绑定权限成功"""
        # 先创建角色和权限
        import uuid

        unique_suffix = uuid.uuid4().hex[:8].lower()

        role_data = {
            "code": f"perm_bind_role_{unique_suffix}",
            "name": f"权限绑定角色_{unique_suffix}",
            "description": "用于权限绑定测试的角色",
        }
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        assert role_response.status_code == 200
        role_id = role_response.json()["data"]["id"]

        permission_data = {
            "code": f"test:bind_perm_{unique_suffix}",
            "name": f"测试绑定权限_{unique_suffix}",
            "description": "用于绑定测试的权限",
        }
        perm_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert perm_response.status_code == 200
        perm_id = perm_response.json()["data"]["id"]

        # 绑定权限
        bind_data = {"role_id": role_id, "target_ids": [perm_id]}
        response = client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_bind_permissions_role_not_exist(self, client: TestClient, auth_headers: dict[str, str]):
        """测试绑定权限 - 角色不存在"""
        # 先创建一个权限
        import uuid

        unique_suffix = uuid.uuid4().hex[:8].lower()
        perm_data = {
            "code": f"test:nonexist_role_{unique_suffix}",
            "name": f"测试权限_{unique_suffix}",
            "description": "用于测试的权限",
        }
        perm_response = client.post("/api/v1/permissions/", json=perm_data, headers=auth_headers)
        assert perm_response.status_code == 200, f"权限创建失败: {perm_response.text}"
        perm_id = perm_response.json()["data"]["id"]

        # 使用不存在的角色ID
        bind_data = {"role_id": 999999, "target_ids": [perm_id]}
        response = client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)
        assert response.status_code == 404  # 角色不存在应该返回404

    def test_bind_permissions_batch_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量绑定权限成功"""
        # 创建多个角色
        role_data_1 = {
            "code": "batch_perm_role1",
            "name": "批量权限角色1",
            "description": "用于批量权限绑定测试的角色1",
        }
        role_data_2 = {
            "code": "batch_perm_role2",
            "name": "批量权限角色2",
            "description": "用于批量权限绑定测试的角色2",
        }
        role1_response = client.post("/api/v1/roles/", json=role_data_1, headers=auth_headers)
        role2_response = client.post("/api/v1/roles/", json=role_data_2, headers=auth_headers)
        role1_id = role1_response.json()["data"]["id"]
        role2_id = role2_response.json()["data"]["id"]

        # 创建权限
        permission_data = {"code": "test:batch_perm", "name": "测试批量权限", "description": "用于批量绑定测试的权限"}
        perm_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        perm_id = perm_response.json()["data"]["id"]

        # 批量绑定权限（改为循环调用单个绑定端点）
        for rid in [role1_id, role2_id]:
            bind_data = {"role_id": rid, "target_ids": [perm_id]}
            response = client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_unbind_permissions_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试解绑权限成功"""
        # 先创建角色和权限并绑定
        role_data = {"code": "perm_unbind_role", "name": "权限解绑角色", "description": "用于权限解绑测试的角色"}
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = role_response.json()["data"]["id"]

        permission_data = {"code": "test:unbind_perm", "name": "测试解绑权限", "description": "用于解绑测试的权限"}
        perm_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        perm_id = perm_response.json()["data"]["id"]

        # 先绑定
        bind_data = {"role_id": role_id, "target_ids": [perm_id]}
        client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)

        # 解绑权限
        unbind_data = {"role_id": role_id, "target_ids": [perm_id]}
        response = client.post("/api/v1/roles/unbind-permissions", json=unbind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_unbind_permissions_batch_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量解绑权限成功"""
        # 创建多个角色
        role_data_1 = {
            "code": "unbatch_perm_role1",
            "name": "批量解绑权限角色1",
            "description": "用于批量权限解绑测试的角色1",
        }
        role_data_2 = {
            "code": "unbatch_perm_role2",
            "name": "批量解绑权限角色2",
            "description": "用于批量权限解绑测试的角色2",
        }
        role1_response = client.post("/api/v1/roles/", json=role_data_1, headers=auth_headers)
        role2_response = client.post("/api/v1/roles/", json=role_data_2, headers=auth_headers)
        role1_id = role1_response.json()["data"]["id"]
        role2_id = role2_response.json()["data"]["id"]

        # 创建权限
        permission_data = {
            "code": "test:unbatch_perm",
            "name": "测试批量解绑权限",
            "description": "用于批量解绑测试的权限",
        }
        perm_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        perm_id = perm_response.json()["data"]["id"]

        # 先绑定（改为循环调用单个绑定端点）
        for rid in [role1_id, role2_id]:
            bind_data = {"role_id": rid, "target_ids": [perm_id]}
            client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)

        # 批量解绑（改为循环调用单个解绑端点）
        for rid in [role1_id, role2_id]:
            unbind_data = {"role_id": rid, "target_ids": [perm_id]}
            response = client.post("/api/v1/roles/unbind-permissions", json=unbind_data, headers=auth_headers)
        assert response.status_code == 200

    def test_bind_permissions_without_auth(self, client: TestClient):
        """测试未认证绑定权限"""
        bind_data = {"role_id": 1, "target_ids": [1]}
        response = client.post("/api/v1/roles/bind-permissions", json=bind_data)
        assert response.status_code == 401

    def test_unbind_permissions_without_auth(self, client: TestClient):
        """测试未认证解绑权限"""
        unbind_data = {"role_id": 1, "target_ids": [1]}
        response = client.post("/api/v1/roles/unbind-permissions", json=unbind_data)
        assert response.status_code == 401
