"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_roles.py
@DateTime: 2025/08/26 15:30:00
@Docs: 角色管理API测试
"""

from fastapi.testclient import TestClient


class TestRoles:
    """角色管理API测试"""

    def test_create_role_success(self, client: TestClient, auth_headers: dict[str, str], test_role_data: dict):
        """测试创建角色成功"""
        response = client.post("/api/v1/roles/", json=test_role_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["code"] == test_role_data["code"]
        assert data["data"]["name"] == test_role_data["name"]

    def test_create_role_duplicate_code(self, client: TestClient, auth_headers: dict[str, str]):
        """测试创建角色 - 代码重复"""
        role_data = {
            "code": "super_admin",  # 已存在的角色代码
            "name": "重复角色",
            "description": "重复的角色代码",
        }
        response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        assert response.status_code == 409

    def test_create_role_without_auth(self, client: TestClient, test_role_data: dict):
        """测试未认证创建角色"""
        response = client.post("/api/v1/roles/", json=test_role_data)
        assert response.status_code == 401

    def test_create_role_missing_required_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试创建角色 - 缺少必填字段"""
        incomplete_data = {
            "name": "不完整角色"
            # 缺少 code 字段
        }
        response = client.post("/api/v1/roles/", json=incomplete_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_role_detail(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取角色详情"""
        # 先创建一个角色
        role_data = {"code": "detail_role", "name": "详情角色", "description": "用于测试详情的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 获取角色详情
        response = client.get(f"/api/v1/roles/{role_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["code"] == role_data["code"]

    def test_get_role_detail_not_found(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取不存在的角色详情"""
        response = client.get("/api/v1/roles/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_list_roles(self, client: TestClient, auth_headers: dict[str, str]):
        """测试分页查询角色列表"""
        response = client.get("/api/v1/roles/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "page_size" in data["data"]

    def test_update_role_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新角色成功"""
        # 先创建一个角色
        role_data = {"code": "update_role", "name": "更新角色", "description": "用于测试更新的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 更新角色
        update_data = {"name": "已更新角色", "description": "角色已更新"}
        response = client.put(f"/api/v1/roles/{role_id}?version=0", json=update_data, headers=auth_headers)
        assert response.status_code == 200

    def test_update_role_version_conflict(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新角色 - 版本冲突"""
        # 先创建一个角色
        role_data = {"code": "conflict_role", "name": "冲突角色", "description": "用于测试冲突的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 使用错误的版本号更新
        update_data = {"name": "冲突更新"}
        response = client.put(f"/api/v1/roles/{role_id}?version=999", json=update_data, headers=auth_headers)
        assert response.status_code == 409

    def test_delete_role_soft(self, client: TestClient, auth_headers: dict[str, str]):
        """测试软删除角色"""
        # 先创建一个角色
        role_data = {"code": "delete_role", "name": "删除角色", "description": "用于测试删除的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 软删除角色
        response = client.delete(f"/api/v1/roles/{role_id}?hard=false", headers=auth_headers)
        assert response.status_code == 200

    def test_delete_role_hard(self, client: TestClient, auth_headers: dict[str, str]):
        """测试硬删除角色"""
        # 先创建一个角色
        role_data = {"code": "hard_delete_role", "name": "硬删除角色", "description": "用于测试硬删除的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 硬删除角色
        response = client.delete(f"/api/v1/roles/{role_id}?hard=true", headers=auth_headers)
        assert response.status_code == 200

    def test_bulk_delete_roles_soft(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量软删除角色"""
        # 创建多个角色
        roles_to_delete = []
        for i in range(2):
            role_data = {
                "code": f"bulk_delete_role_{i}",
                "name": f"批量删除角色{i}",
                "description": f"用于批量删除测试的角色{i}",
            }
            response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
            roles_to_delete.append(response.json()["data"]["id"])

        # 批量软删除
        response = client.post("/api/v1/roles/delete", json={"ids": roles_to_delete}, headers=auth_headers)
        assert response.status_code == 200

    def test_bulk_delete_roles_hard(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量硬删除角色"""
        # 创建多个角色
        roles_to_delete = []
        for i in range(2):
            role_data = {
                "code": f"bulk_hard_delete_role_{i}",
                "name": f"批量硬删除角色{i}",
                "description": f"用于批量硬删除测试的角色{i}",
            }
            response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
            roles_to_delete.append(response.json()["data"]["id"])

        # 批量硬删除
        response = client.post("/api/v1/roles/delete/hard", json={"ids": roles_to_delete}, headers=auth_headers)
        assert response.status_code == 200

    def test_disable_roles(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量禁用角色"""
        # 先创建一个角色
        role_data = {"code": "disable_role", "name": "禁用角色", "description": "用于测试禁用的角色"}
        create_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = create_response.json()["data"]["id"]

        # 禁用角色
        response = client.post("/api/v1/roles/disable", json={"ids": [role_id]}, headers=auth_headers)
        assert response.status_code == 200

    def test_get_role_users(self, client: TestClient, auth_headers: dict[str, str]):
        """测试查看角色下的用户"""
        # 先创建角色和用户，并绑定
        role_data = {"code": "users_role", "name": "用户角色", "description": "包含用户的角色"}
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        role_id = role_response.json()["data"]["id"]

        user_data = {
            "username": "roleuser",
            "phone": "13900000020",
            "email": "roleuser@example.com",
            "password": "test@123",
            "nickname": "角色用户",
        }
        user_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = user_response.json()["data"]["id"]

        # 绑定用户到角色
        bind_data = {"user_id": user_id, "role_ids": [role_id]}
        client.post("/api/v1/users/bind-roles", json=bind_data, headers=auth_headers)

        # 查看角色下的用户
        response = client.get(f"/api/v1/roles/{role_id}/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
