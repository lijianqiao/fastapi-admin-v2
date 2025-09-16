"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: test_system_config_api.py
@DateTime: 2025/08/27 12:56:24
@Docs: 系统配置 API 测试：
- GET 返回 version 与字段
- PUT 使用乐观锁（version）成功更新会自增版本
- 旧版本提交返回 409 冲突
"""

from fastapi.testclient import TestClient


def test_system_config_get_returns_version_and_fields(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 首次 GET，若不存在会创建默认记录
    r = client.get("/api/v1/system/config", headers=auth_headers)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, dict)
    assert body.get("code") == 200
    data = body.get("data") or {}
    assert isinstance(data.get("version"), int)
    assert "project" in data and "pagination" in data and "password_policy" in data and "login_security" in data


def test_system_config_update_version_increment(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 先获取当前配置与版本
    r1 = client.get("/api/v1/system/config", headers=auth_headers)
    assert r1.status_code == 200
    data1 = r1.json()["data"]
    v1 = int(data1["version"])

    # 执行更新（变更 page_size）
    payload = {"version": v1, "pagination": {"page_size": (data1["pagination"]["page_size"] or 20) + 1}}
    r2 = client.put("/api/v1/system/config", json=payload, headers=auth_headers)
    assert r2.status_code == 200
    data2 = r2.json()["data"]
    v2 = int(data2["version"])
    assert v2 == v1 + 1
    assert data2["pagination"]["page_size"] == payload["pagination"]["page_size"]


def test_system_config_update_conflict_on_stale_version(client: TestClient, auth_headers: dict[str, str]) -> None:
    # 拿到当前最新版本
    r1 = client.get("/api/v1/system/config", headers=auth_headers)
    cur_version = int(r1.json()["data"]["version"])

    # 先用正确版本更新到下一版
    ok_payload = {"version": cur_version, "project": {"name": "CfgName"}}
    r_ok = client.put("/api/v1/system/config", json=ok_payload, headers=auth_headers)
    assert r_ok.status_code == 200
    new_version = int(r_ok.json()["data"]["version"])
    assert new_version == cur_version + 1

    # 再用旧版本提交，应返回 409
    stale_payload = {"version": cur_version, "project": {"description": "stale"}}
    r_conflict = client.put("/api/v1/system/config", json=stale_payload, headers=auth_headers)
    assert r_conflict.status_code == 409
