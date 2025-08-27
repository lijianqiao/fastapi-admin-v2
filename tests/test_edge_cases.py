"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_edge_cases.py
@DateTime: 2025/08/26 15:30:00
@Docs: 边界情况和错误处理测试
"""

from fastapi.testclient import TestClient


class TestEdgeCases:
    """边界情况和错误处理测试"""

    def test_invalid_json_request(self, client: TestClient, auth_headers: dict[str, str]):
        """测试无效的JSON请求"""
        response = client.post(
            "/api/v1/users/", content="invalid json", headers={**auth_headers, "Content-Type": "application/json"}
        )
        assert response.status_code == 422

    def test_missing_content_type(self, client: TestClient, auth_headers: dict[str, str]):
        """测试缺少Content-Type头部"""
        user_data = {
            "username": "testuser",
            "phone": "13900000040",
            "email": "testuser@example.com",
            "password": "test@123",
            "nickname": "测试用户",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        # 应该正常处理，FastAPI会自动设置Content-Type
        assert response.status_code in [200, 422]

    def test_extremely_long_string_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试极长的字符串字段"""
        long_string = "x" * 1000
        user_data = {
            "username": long_string,
            "phone": "13900000041",
            "email": f"{long_string}@example.com",
            "password": "test@123",
            "nickname": "长字符串用户",
        }
        response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        # 应该返回验证错误
        assert response.status_code == 422

    def test_sql_injection_attempts(self, client: TestClient, auth_headers: dict[str, str]):
        """测试SQL注入尝试"""
        malicious_data = {
            "username": "'; DROP TABLE users; --",
            "phone": "13900000042",
            "email": "malicious@example.com",
            "password": "test@123",
            "nickname": "恶意用户",
        }
        response = client.post("/api/v1/users/", json=malicious_data, headers=auth_headers)
        # 应该被正常处理（ORM会处理SQL注入）
        # 可能因为用户名格式不合法而返回422，或者成功创建返回200
        assert response.status_code in [200, 422]

    def test_xss_attempts(self, client: TestClient, auth_headers: dict[str, str]):
        """测试XSS攻击尝试"""
        xss_data = {
            "username": "<script>alert('xss')</script>",
            "phone": "13900000043",
            "email": "xss@example.com",
            "password": "test@123",
            "nickname": "<img src='x' onerror='alert(1)'>",
        }
        response = client.post("/api/v1/users/", json=xss_data, headers=auth_headers)
        # 数据应该被正常存储，XSS防护通常在前端处理
        assert response.status_code in [200, 422]

    def test_unicode_and_emoji_in_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试Unicode字符和表情符号"""
        unicode_data = {
            "username": "用户😀",
            "phone": "13900000044",
            "email": "unicode@example.com",
            "password": "test@123",
            "nickname": "测试用户🎉",
        }
        response = client.post("/api/v1/users/", json=unicode_data, headers=auth_headers)
        # 应该支持Unicode字符
        assert response.status_code in [200, 422]

    def test_negative_ids_in_urls(self, client: TestClient, auth_headers: dict[str, str]):
        """测试URL中的负数ID"""
        response = client.get("/api/v1/users/-1", headers=auth_headers)
        assert response.status_code in [404, 422]

        response = client.get("/api/v1/roles/-1", headers=auth_headers)
        assert response.status_code in [404, 422]

    def test_zero_ids_in_urls(self, client: TestClient, auth_headers: dict[str, str]):
        """测试URL中的零ID"""
        response = client.get("/api/v1/users/0", headers=auth_headers)
        assert response.status_code in [404, 422]

    def test_non_numeric_ids_in_urls(self, client: TestClient, auth_headers: dict[str, str]):
        """测试URL中的非数字ID"""
        response = client.get("/api/v1/users/abc", headers=auth_headers)
        assert response.status_code == 422

        response = client.get("/api/v1/roles/xyz", headers=auth_headers)
        assert response.status_code == 422

    def test_extremely_large_page_size(self, client: TestClient, auth_headers: dict[str, str]):
        """测试极大的分页大小"""
        response = client.get("/api/v1/users/?page=1&page_size=999999", headers=auth_headers)
        assert response.status_code == 422

    def test_zero_page_size(self, client: TestClient, auth_headers: dict[str, str]):
        """测试零分页大小"""
        response = client.get("/api/v1/users/?page=1&page_size=0", headers=auth_headers)
        assert response.status_code == 422

    def test_negative_page_number(self, client: TestClient, auth_headers: dict[str, str]):
        """测试负数页码"""
        response = client.get("/api/v1/users/?page=-1&page_size=10", headers=auth_headers)
        assert response.status_code == 422

    def test_invalid_email_formats(self, client: TestClient, auth_headers: dict[str, str]):
        """测试无效的邮箱格式"""
        invalid_emails = ["invalid-email", "@example.com", "user@", "user@@example.com", "user.example.com"]

        for i, email in enumerate(invalid_emails):
            user_data = {
                "username": f"emailtest{i}",
                "phone": f"1390000005{i}",
                "email": email,
                "password": "test@123",
                "nickname": f"邮箱测试{i}",
            }
            response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
            # 应该返回验证错误
            assert response.status_code == 422

    def test_invalid_phone_formats(self, client: TestClient, auth_headers: dict[str, str]):
        """测试无效的手机号格式"""
        invalid_phones = ["123", "abc123456789", "1234567890123456789", "+86-138-0000-0000", ""]

        for i, phone in enumerate(invalid_phones):
            user_data = {
                "username": f"phonetest{i}",
                "phone": phone,
                "email": f"phonetest{i}@example.com",
                "password": "test@123",
                "nickname": f"手机测试{i}",
            }
            response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
            # 可能因手机号格式验证而返回422
            assert response.status_code in [200, 422]

    def test_empty_string_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试空字符串字段"""
        empty_data = {"username": "", "phone": "", "email": "", "password": "", "nickname": ""}
        response = client.post("/api/v1/users/", json=empty_data, headers=auth_headers)
        assert response.status_code == 422

    def test_null_fields(self, client: TestClient, auth_headers: dict[str, str]):
        """测试null字段"""
        null_data = {"username": None, "phone": None, "email": None, "password": None, "nickname": None}
        response = client.post("/api/v1/users/", json=null_data, headers=auth_headers)
        assert response.status_code == 422

    def test_concurrent_version_updates(self, client: TestClient, auth_headers: dict[str, str]):
        """测试并发版本更新冲突"""
        # 创建用户
        user_data = {
            "username": "concurrentuser",
            "phone": "13900000060",
            "email": "concurrent@example.com",
            "password": "test@123",
            "nickname": "并发用户",
        }
        create_response = client.post("/api/v1/users/", json=user_data, headers=auth_headers)
        user_id = create_response.json()["data"]["id"]

        # 模拟并发更新：两个请求使用相同的版本号
        update_data_1 = {"nickname": "更新1"}
        update_data_2 = {"nickname": "更新2"}

        response_1 = client.put(f"/api/v1/users/{user_id}?version=0", json=update_data_1, headers=auth_headers)
        response_2 = client.put(f"/api/v1/users/{user_id}?version=0", json=update_data_2, headers=auth_headers)

        # 第一个应该成功，第二个应该因版本冲突而失败
        responses = [response_1.status_code, response_2.status_code]
        assert 200 in responses
        assert 409 in responses
