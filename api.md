### 标准 API 文档（v1）

- 基础 URL：`http://127.0.0.1:8000`
- 业务前缀：`/api/v1`

### 全局约定
- 鉴权：除登录与刷新外，均需 `Authorization: Bearer <access_token>`
- 统一响应（除登录/刷新外）：
```json
{ "code": 200, "message": "success", "data": any }
```
- 校验失败：`422`，返回统一错误结构
- 分页参数：`page`(>=1, 默认1)、`page_size`(1~200, 默认20)
- 乐观锁：所有更新操作均在请求体 JSON 中携带 `version`（用户/角色/权限、系统配置一致）。

---

## 认证 Auth

- 登录（表单）
  - POST `/api/v1/auth/login`
  - Content-Type: `application/x-www-form-urlencoded`
  - Body：`username`、`password`
  - 200：
    ```json
    { "access_token": "xxx", "token_type": "bearer", "refresh_token": "xxx" }
    ```

- 刷新令牌
  - POST `/api/v1/auth/refresh`
  - JSON：`{ "refresh_token": "xxx" }`
  - 200：同登录返回

- 注销（令牌版本自增，旧令牌失效）
  - POST `/api/v1/auth/logout`
  - 需要登录，无请求体
  - 200：
    ```json
    { "code":200, "message":"success", "data": { "msg": "注销成功" } }
    ```

---

## 用户 Users

- 获取当前用户
  - GET `/api/v1/users/me`
  - 需要登录

- 自助修改密码
  - POST `/api/v1/users/me/password`
  - JSON：`{ "old_password": "", "new_password": "", "confirm_password": "" }`

- 创建用户（user:create）
  - POST `/api/v1/users/`
  - JSON（必填）：
    ```json
    { "username":"u1", "phone":"13900000000", "email":"u1@example.com", "password":"pass@123", "nickname":"u1" }
    ```

- 更新用户（user:update，乐观锁）
  - PUT `/api/v1/users/{user_id}`
  - JSON（必须包含 `version`，其余可选）：`{ "version": 1, "username"?, "phone"?, "email"?, "password"?, "is_active"?, "nickname"?, "bio"?, "avatar_url"? }`

- 获取用户详情（user:list）
  - GET `/api/v1/users/{user_id}`

- 分页列表（user:list）
  - GET `/api/v1/users/?keyword=&page=1&page_size=20`

- 删除用户（默认软删）（user:delete）
  - DELETE `/api/v1/users/{user_id}?hard=false`
  
- 批量删除（支持软/硬删）（user:bulk_delete）
  - POST `/api/v1/users/delete?hard=false|true`
  - JSON：`{ "ids": [1,2,3] }`

- 批量禁用（user:disable）
  - POST `/api/v1/users/disable`
  - JSON：`{ "ids": [1,2,3] }`

- 管理员修改用户密码（user:update）
  - POST `/api/v1/users/{user_id}/password`
  - JSON：`{ "new_password": "", "confirm_password": "" }`

- 解锁用户（user:unlock）
  - POST `/api/v1/users/{user_id}/unlock`

- 绑定角色（user:bind_roles）
  - POST `/api/v1/users/bind-roles`
  - JSON：`{ "user_id": 1, "role_ids": [1,2] }`
  - 返回：`Response<BindStats>`（added/restored/existed）

- 解绑角色（user:unbind_roles）
  - POST `/api/v1/users/unbind-roles`
  - JSON 同绑定

---

## 角色 Roles

- 创建角色（role:create）
  - POST `/api/v1/roles/`
  - JSON：`{ "code":"admin", "name":"管理员", "description": "..." }`

- 更新角色（role:update，乐观锁）
  - PUT `/api/v1/roles/{role_id}`
  - JSON（必须包含 `version`，其余可选）：`{ "version": 1, "name"?, "code"?, "is_active"?, "description"? }`

- 获取角色详情（role:list）
  - GET `/api/v1/roles/{role_id}`

- 分页列表（role:list）
  - GET `/api/v1/roles/?page=1&page_size=20`

- 删除角色（默认软删）（role:delete）
  - DELETE `/api/v1/roles/{role_id}?hard=false`
  
- 批量删除（支持软/硬删）（role:bulk_delete）
  - POST `/api/v1/roles/delete?hard=false|true`
  - JSON：`{ "ids": [1,2,3] }`

- 批量禁用（role:disable）
  - POST `/api/v1/roles/disable`
  - JSON：`{ "ids": [1,2,3] }`

- 查看角色下的用户（user:list）
  - GET `/api/v1/roles/{role_id}/users?page=1&page_size=20`

- 绑定权限（role:bind_permissions）
  - POST `/api/v1/roles/bind-permissions`
  - JSON：`{ "role_id": 1, "target_ids": [1,2] }`
  - 返回：`Response<BindStats>`
  - 返回：`Response<BindStats>`

- 解绑权限（role:unbind_permissions）
  - POST `/api/v1/roles/unbind-permissions`

---

## 权限 Permissions

- 创建权限（permission:create）
  - POST `/api/v1/permissions/`
  - JSON：`{ "code":"user:list", "name":"用户列表", "description":"..." }`

- 更新权限（permission:update，乐观锁）
  - PUT `/api/v1/permissions/{perm_id}`
  - JSON（必须包含 `version`，其余可选）：`{ "version": 1, "code"?, "name"?, "description"?, "is_active"? }`

- 获取权限详情（permission:list）
  - GET `/api/v1/permissions/{perm_id}`

- 分页列表（permission:list）
  - GET `/api/v1/permissions/?page=1&page_size=20`

- 删除权限（默认软删）（permission:delete）
  - DELETE `/api/v1/permissions/{perm_id}?hard=false`
  
- 批量删除（支持软/硬删）（permission:bulk_delete）
  - POST `/api/v1/permissions/delete?hard=false|true`
  - JSON：`{ "ids": [1,2,3] }`

- 批量禁用（permission:disable）
  - POST `/api/v1/permissions/disable`
  - JSON：`{ "ids": [1,2,3] }`

- 查看拥有该权限的角色（role:list）
  - GET `/api/v1/permissions/{perm_id}/roles?page=1&page_size=20`

---

## 审计日志 Logs

- 分页查询（log:list）
  - GET `/api/v1/logs/?actor_id=&action=&trace_id=&page=1&page_size=20`

- 我的操作记录（需登录）
  - GET `/api/v1/logs/me?page=1&page_size=20`

---

## 系统 System

- 健康检查
  - GET `/api/health`

- 指标（Prometheus）
  - GET `/metrics`
  - 受 `METRICS_ALLOW_IPS` 限制

---

## 系统配置 System Config

- 获取系统配置（system:config:read）
  - GET `/api/v1/system/config`
  - 200：
    ```json
    {
      "code": 200,
      "message": "success",
      "data": {
        "version": 3,
        "project": { "name": "FastAPIAdmin", "description": "...", "url": null },
        "pagination": { "page_size": 20 },
        "password_policy": {
          "min_length": 8,
          "require_uppercase": false,
          "require_lowercase": false,
          "require_digits": false,
          "require_special": false,
          "expire_days": 0
        },
        "login_security": {
          "max_failed_attempts": 5,
          "lock_minutes": 3,
          "session_timeout_hours": 0,
          "force_https": false
        }
      }
    }
    ```

- 更新系统配置（system:config:update，乐观锁）
  - PUT `/api/v1/system/config`
  - JSON：必须包含 `version`，并可任选一到多个设置块
    ```json
    {
      "version": 3,
      "project": { "name": "My Admin" },
      "pagination": { "page_size": 30 },
      "password_policy": {
        "min_length": 10,
        "require_uppercase": true,
        "require_lowercase": true,
        "require_digits": true,
        "require_special": false,
        "expire_days": 0
      },
      "login_security": { "max_failed_attempts": 5, "lock_minutes": 3, "session_timeout_hours": 6, "force_https": false }
    }
    ```
  - 200：返回最新配置（`version` 自增）
  - 409：当提交的 `version` 落后于当前版本，返回冲突错误，需先重新 GET 获取最新 `version` 再提交

---

## 数据模型（摘要）

- TokenOut：`{ access_token: string, token_type: "bearer", refresh_token?: string }`
- Response<T>：`{ code: number, message: string, data: T | null }`
- Page<T>：`{ items: T[], total: number, page: number, page_size: number }`
- BindStats：`{ added: number, restored: number, existed: number }`

---

## OpenAPI/Swagger
- OpenAPI：`GET /openapi.json`
- Swagger UI：`/docs`
- ReDoc：`/redoc`