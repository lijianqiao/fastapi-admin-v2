"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_permissions.py
@DateTime: 2025/08/26 15:30:00
@Docs: 权限管理API测试
"""

from fastapi.testclient import TestClient


class TestPermissions:
    """权限管理API测试"""

    def test_create_permission_success(
        self, client: TestClient, auth_headers: dict[str, str], test_permission_data: dict
    ):
        """测试创建权限成功"""
        response = client.post("/api/v1/permissions/", json=test_permission_data, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["code"] == test_permission_data["code"]
        assert data["data"]["name"] == test_permission_data["name"]

    def test_create_permission_duplicate_code(self, client: TestClient, auth_headers: dict[str, str]):
        """测试创建权限 - 代码重复"""
        permission_data = {
            "code": "user:list",  # 已存在的权限代码
            "name": "重复权限",
            "description": "重复的权限代码",
        }
        response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert response.status_code == 409

    def test_create_permission_without_auth(self, client: TestClient, test_permission_data: dict):
        """测试未认证创建权限"""
        response = client.post("/api/v1/permissions/", json=test_permission_data)
        assert response.status_code == 401

    def test_create_permission_missing_required_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试创建权限 - 缺少必填字段"""
        incomplete_data = {
            "name": "不完整权限"
            # 缺少 code 字段
        }
        response = client.post("/api/v1/permissions/", json=incomplete_data, headers=auth_headers)
        assert response.status_code == 422

    def test_get_permission_detail(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取权限详情"""
        # 先创建一个权限
        permission_data = {"code": "test:detail_perm", "name": "详情权限", "description": "用于测试详情的权限"}
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        perm_id = create_response.json()["data"]["id"]

        # 获取权限详情
        response = client.get(f"/api/v1/permissions/{perm_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert data["data"]["code"] == permission_data["code"]

    def test_get_permission_detail_not_found(self, client: TestClient, auth_headers: dict[str, str]):
        """测试获取不存在的权限详情"""
        response = client.get("/api/v1/permissions/999999", headers=auth_headers)
        assert response.status_code == 404

    def test_list_permissions(self, client: TestClient, auth_headers: dict[str, str]):
        """测试分页查询权限列表"""
        response = client.get("/api/v1/permissions/?page=1&page_size=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]
        assert "page_size" in data["data"]

    def test_update_permission_success(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新权限成功"""
        # 先创建一个权限
        import uuid

        unique_suffix = uuid.uuid4().hex[:8].lower()
        permission_data = {
            "code": f"test:update_perm_{unique_suffix}",
            "name": f"更新权限_{unique_suffix}",
            "description": "用于测试更新的权限",
        }
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert create_response.status_code == 200, f"权限创建失败: {create_response.text}"
        perm_id = create_response.json()["data"]["id"]

        # 更新权限
        update_data = {"name": "已更新权限", "description": "权限已更新"}
        response = client.put(f"/api/v1/permissions/{perm_id}?version=0", json=update_data, headers=auth_headers)
        assert response.status_code == 200

    def test_update_permission_version_conflict(self, client: TestClient, auth_headers: dict[str, str]):
        """测试更新权限 - 版本冲突"""
        # 先创建一个权限
        import uuid

        unique_code = f"test:conflict_perm_{uuid.uuid4().hex[:8].lower()}"
        permission_data = {
            "code": unique_code,
            "name": f"冲突权限_{uuid.uuid4().hex[:8]}",
            "description": "用于测试冲突的权限",
        }
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert create_response.status_code == 200
        perm_id = create_response.json()["data"]["id"]

        # 使用错误的版本号更新
        update_data = {"name": "冲突更新"}
        response = client.put(f"/api/v1/permissions/{perm_id}?version=999", json=update_data, headers=auth_headers)
        assert response.status_code == 409

    def test_delete_permission_soft(self, client: TestClient, auth_headers: dict[str, str]):
        """测试软删除权限"""
        # 先创建一个权限
        import uuid

        unique_code = f"test:delete_perm_{uuid.uuid4().hex[:8].lower()}"
        permission_data = {
            "code": unique_code,
            "name": f"删除权限_{uuid.uuid4().hex[:8]}",
            "description": "用于测试删除的权限",
        }
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert create_response.status_code == 200
        perm_id = create_response.json()["data"]["id"]

        # 软删除权限
        response = client.delete(f"/api/v1/permissions/{perm_id}?hard=false", headers=auth_headers)
        assert response.status_code == 200

    def test_delete_permission_hard(self, client: TestClient, auth_headers: dict[str, str]):
        """测试硬删除权限"""
        # 先创建一个权限
        import uuid

        unique_code = f"test:hard_delete_perm_{uuid.uuid4().hex[:8].lower()}"
        permission_data = {
            "code": unique_code,
            "name": f"硬删除权限_{uuid.uuid4().hex[:8]}",
            "description": "用于测试硬删除的权限",
        }
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert create_response.status_code == 200
        perm_id = create_response.json()["data"]["id"]

        # 硬删除权限
        response = client.delete(f"/api/v1/permissions/{perm_id}?hard=true", headers=auth_headers)
        assert response.status_code == 200

    def test_bulk_delete_permissions_soft(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量软删除权限"""
        # 创建多个权限
        import uuid

        perms_to_delete = []
        for i in range(2):
            unique_code = f"test:bulk_delete_perm_{i}_{uuid.uuid4().hex[:8].lower()}"
            permission_data = {
                "code": unique_code,
                "name": f"批量删除权限{i}_{uuid.uuid4().hex[:8]}",
                "description": f"用于批量删除测试的权限{i}",
            }
            response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
            assert response.status_code == 200
            perms_to_delete.append(response.json()["data"]["id"])

        # 批量软删除
        response = client.post("/api/v1/permissions/delete", json={"ids": perms_to_delete}, headers=auth_headers)
        assert response.status_code == 200

    def test_bulk_delete_permissions_hard(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量硬删除权限"""
        # 创建多个权限
        import uuid

        perms_to_delete = []
        for i in range(2):
            unique_code = f"test:bulk_hard_delete_perm_{i}_{uuid.uuid4().hex[:8].lower()}"
            permission_data = {
                "code": unique_code,
                "name": f"批量硬删除权限{i}_{uuid.uuid4().hex[:8]}",
                "description": f"用于批量硬删除测试的权限{i}",
            }
            response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
            assert response.status_code == 200
            perms_to_delete.append(response.json()["data"]["id"])

        # 批量硬删除
        response = client.post("/api/v1/permissions/delete/hard", json={"ids": perms_to_delete}, headers=auth_headers)
        assert response.status_code == 200

    def test_disable_permissions(self, client: TestClient, auth_headers: dict[str, str]):
        """测试批量禁用权限"""
        # 先创建一个权限
        import uuid

        unique_code = f"test:disable_perm_{uuid.uuid4().hex[:8].lower()}"
        permission_data = {
            "code": unique_code,
            "name": f"禁用权限_{uuid.uuid4().hex[:8]}",
            "description": "用于测试禁用的权限",
        }
        create_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert create_response.status_code == 200
        perm_id = create_response.json()["data"]["id"]

        # 禁用权限
        response = client.post("/api/v1/permissions/disable", json={"ids": [perm_id]}, headers=auth_headers)
        assert response.status_code == 200

    def test_get_permission_roles(self, client: TestClient, auth_headers: dict[str, str]):
        """测试查看拥有该权限的角色"""
        # 先创建权限和角色，并绑定
        import uuid

        unique_perm_code = f"test:roles_perm_{uuid.uuid4().hex[:8].lower()}"
        permission_data = {
            "code": unique_perm_code,
            "name": f"角色权限_{uuid.uuid4().hex[:8]}",
            "description": "包含角色的权限",
        }
        perm_response = client.post("/api/v1/permissions/", json=permission_data, headers=auth_headers)
        assert perm_response.status_code == 200
        perm_id = perm_response.json()["data"]["id"]

        unique_role_code = f"perm_role_{uuid.uuid4().hex[:8].lower()}"
        role_data = {
            "code": unique_role_code,
            "name": f"权限角色_{uuid.uuid4().hex[:8]}",
            "description": "拥有权限的角色",
        }
        role_response = client.post("/api/v1/roles/", json=role_data, headers=auth_headers)
        assert role_response.status_code == 200
        role_id = role_response.json()["data"]["id"]

        # 绑定权限到角色
        bind_data = {"role_id": role_id, "target_ids": [perm_id]}
        bind_response = client.post("/api/v1/roles/bind-permissions", json=bind_data, headers=auth_headers)
        assert bind_response.status_code == 200

        # 查看权限的角色
        response = client.get(f"/api/v1/permissions/{perm_id}/roles", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 200
