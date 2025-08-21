### API 文档（v1）

基础 URL： `http://127.0.0.1:8000/api`
版本： `/v1`

本项目所有非登录接口均返回统一响应：
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```
- 认证失败等 HTTP 异常：`code = http_status` 且 `data = null`
- 验证错误 422：
```json
{
  "code": 422,
  "message": "字段级友好提示",
  "data": [{ "field": "xxx", "message": "xxx", "type": "xxx" }]
}
```
- 认证头：`Authorization: Bearer <access_token>`
- 分页：query 参数 `page`(>=1)，`page_size`(1~200)

---

## 认证 Auth

- 登录（OAuth2 表单）
  - POST `/api/v1/auth/login`
  - Content-Type: `application/x-www-form-urlencoded`
  - Body: `username`, `password`
  - 200:
    ```json
    { "access_token": "xxx", "token_type": "bearer", "refresh_token": "xxx" }
    ```

- 刷新令牌
  - POST `/api/v1/auth/refresh`
  - Body:
    ```json
    { "refresh_token": "xxx" }
    ```
  - 200 同登录返回结构

- 注销（令牌版本自增，旧令牌全失效）
  - POST `/api/v1/auth/logout`
  - Query: `user_id`(int)

---

## 用户 Users

- 获取当前用户详情（需登录，无需额外权限）
  - GET `/api/v1/users/me`
  - 200.data:
    ```json
    {
      "id": 1, "version": 0, "username": "admin", "phone": "13800000000",
      "email": "admin@example.com", "is_active": true,
      "failed_attempts": 0, "locked_until": null, "last_login_at": "2025-08-21T...",
      "created_at": "2025-08-21T..."
    }
    ```

- 用户自助修改密码（需登录，无需额外权限）
  - POST `/api/v1/users/me/password`
  - Body:
    ```json
    { "old_password": "xxx", "new_password": "xxx", "confirm_password": "xxx" }
    ```

- 创建用户
  - POST `/api/v1/users/`
  - 权限：`user:create`
  - Body:
    ```json
    { "username": "u1", "phone": "13900000001", "password": "pass@123", "email": "x@x.com" }
    ```
  - 200.data: UserOut

- 更新用户（乐观锁）
  - PUT `/api/v1/users/{user_id}`
  - 权限：`user:update`
  - Query: `version`(int, 必填)
  - Body（部分字段可选）:
    ```json
    { "username": "new", "phone": "13900000002", "email": "x@x.com", "password": "new", "is_active": true }
    ```

- 获取用户详情
  - GET `/api/v1/users/{user_id}`
  - 权限：`user:list`
  - 200.data: UserOut

- 分页用户列表
  - GET `/api/v1/users/?keyword=&page=1&page_size=20`
  - 权限：`user:list`
  - 200.data:
    ```json
    {
      "items": [UserOut...], "total": 123, "page": 1, "page_size": 20
    }
    ```

- 批量禁用用户
  - POST `/api/v1/users/disable`
  - 权限：`user:disable`
  - Body:
    ```json
    { "ids": [1,2,3] }
    ```

- 为用户绑定角色
  - POST `/api/v1/users/bind-roles`
  - 权限：`user:bind_roles`
  - Body:
    ```json
    { "user_id": 1, "role_ids": [1,2] }
    ```

- 为多个用户批量绑定角色
  - POST `/api/v1/users/bind-roles/batch`
  - 权限：`user:bind_roles_batch`
  - Body:
    ```json
    { "user_ids": [1,2], "role_ids": [1,2] }
    ```

- 为用户移除角色
  - POST `/api/v1/users/unbind-roles`
  - 权限：`user:unbind_roles`
  - Body 同绑定

- 为多个用户批量移除角色
  - POST `/api/v1/users/unbind-roles/batch`
  - 权限：`user:unbind_roles_batch`
  - Body:
    ```json
    { "user_ids": [1,2], "role_ids": [1,2] }
    ```

- 管理员修改指定用户密码
  - POST `/api/v1/users/{user_id}/password`
  - 权限：`user:update`
  - Body:
    ```json
    { "new_password": "xxx", "confirm_password": "xxx" }
    ```

---

## 角色 Roles

- 创建角色
  - POST `/api/v1/roles/`
  - 权限：`role:create`
  - Body:
    ```json
    { "code": "admin", "name": "管理员", "description": "..." }
    ```

- 更新角色（乐观锁）
  - PUT `/api/v1/roles/{role_id}?version=1`
  - 权限：`role:update`
  - Body（部分字段可选）:
    ```json
    { "name": "新名", "code": "new_code", "is_active": true, "description": "..." }
    ```

- 获取角色详情
  - GET `/api/v1/roles/{role_id}`
  - 权限：`role:list`

- 分页角色列表
  - GET `/api/v1/roles/?page=1&page_size=20`
  - 权限：`role:list`

- 批量禁用角色
  - POST `/api/v1/roles/disable`
  - 权限：`role:disable`
  - Body: `{ "ids": [1,2,3] }`

- 绑定权限到角色
  - POST `/api/v1/roles/bind-permissions`
  - 权限：`role:bind_permissions`
  - Body:
    ```json
    { "role_id": 1, "target_ids": [1,2] }
    ```

- 批量绑定权限到多个角色
  - POST `/api/v1/roles/bind-permissions/batch`
  - 权限：`role:bind_permissions_batch`
  - Body:
    ```json
    { "role_ids": [1,2], "permission_ids": [1,2] }
    ```

- 为角色移除权限
  - POST `/api/v1/roles/unbind-permissions`
  - 权限：`role:unbind_permissions`
  - Body 同绑定

- 为多个角色批量移除权限
  - POST `/api/v1/roles/unbind-permissions/batch`
  - 权限：`role:unbind_permissions_batch`
  - Body:
    ```json
    { "role_ids": [1,2], "permission_ids": [1,2] }
    ```

- 查看角色下的用户
  - GET `/api/v1/roles/{role_id}/users?page=1&page_size=20`
  - 权限：`user:list`
  - 200.data: Page[UserOut]

---

## 权限 Permissions

- 创建权限
  - POST `/api/v1/permissions/`
  - 权限：`permission:create`
  - Body:
    ```json
    { "code": "user:list", "name": "用户列表", "description": "..." }
    ```

- 更新权限（乐观锁）
  - PUT `/api/v1/permissions/{perm_id}?version=1`
  - 权限：`permission:update`
  - Body（部分字段可选）:
    ```json
    { "name": "新名", "code": "user:update", "is_active": true, "description": "..." }
    ```

- 获取权限详情
  - GET `/api/v1/permissions/{perm_id}`
  - 权限：`permission:list`

- 分页权限列表
  - GET `/api/v1/permissions/?page=1&page_size=20`
  - 权限：`permission:list`

- 批量禁用权限
  - POST `/api/v1/permissions/disable`
  - 权限：`permission:disable`
  - Body: `{ "ids": [1,2,3] }`

- 查看权限下的角色
  - GET `/api/v1/permissions/{perm_id}/roles?page=1&page_size=20`
  - 权限：`role:list`
  - 200.data: Page[RoleOut]

---

## 审计日志 Logs

- 分页查询审计日志
  - GET `/api/v1/logs/?actor_id=&action=&trace_id=&page=1&page_size=20`
  - 权限：`log:list`
  - 200.data: Page[AuditLogOut]

---

## 系统 System

- 健康检查
  - GET `/api/health`
  - 200: `{}`

---

## 示例 curl

```bash
# 登录
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin@123"

# 带 token 查询当前用户
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/users/me

# 创建用户
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"username":"u1","phone":"13900000001","password":"pass@123"}'
```

---

## 字段与校验（摘录）

- UserCreate
  - username: 长度 3~64
  - phone: `^\d{6,20}$`（如需严格中国大陆手机号可换成 `^1[3-9]\d{9}$`）
  - password: 长度 6~64

- 修改密码
  - AdminChangePasswordIn: new/confirm 一致
  - SelfChangePasswordIn: old/new 不同，new/confirm 一致

- Role.code: `^[a-z0-9_\-]{2,64}$`
- Permission.code: `^[a-z][a-z0-9_]*:[a-z][a-z0-9_]*$`
- 所有批量 IDs：`min_length = 1`，部分去重校验

前端如需 OpenAPI/Swagger 文件：
- OpenAPI JSON：`GET /openapi.json`
- Swagger UI：`/docs`
- ReDoc：`/redoc`