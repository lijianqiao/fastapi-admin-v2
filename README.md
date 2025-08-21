### FastAPI Admin RBAC

基于 FastAPI + Tortoise-ORM + PostgreSQL(Asyncpg) + Redis 的现代化 RBAC 权限管理后端，支持完整的用户/角色/权限/审计日志模块，统一响应、依赖注入、Redis 权限缓存、软删除与乐观锁、批量操作、操作审计、JWT 鉴权（Access/Refresh）。

---

### 技术栈
- Python 3.13、FastAPI、Pydantic v2、Loguru
- Tortoise-ORM、Aerich（迁移）、PostgreSQL + asyncpg
- Redis（权限缓存、令牌版本）

---

### 目录结构（核心）
- app/
  - api/v1/：各模块 REST API
  - core/：配置、数据库、异常、生命周期、权限工具等
  - models/：Tortoise 数据模型（含软删/乐观锁/索引）
  - dao/：DAO 层，封装 CRUD、批量、分页、关系操作
  - services/：服务层，业务编排与审计装饰器
  - schemas/：Pydantic 校验模型与统一响应模型
  - utils/：日志、Redis、审计装饰器、内置 RBAC 数据等

---

### 快速开始
1) 安装依赖
```bash
uv sync
```

2) 配置环境变量（.env）
```ini
# 应用
APP_NAME=FastAPIAdmin
APP_VERSION=0.1.0
APP_DESCRIPTION=基于FastAPI的后台管理系统
API_PREFIX=/api
DEBUG=true
ENVIRONMENT=development  # development/testing/production

# 数据库（PostgreSQL，使用 asyncpg 驱动）
DATABASE_URL=postgres://username:password@localhost:5432/db-name

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=替换为生产密钥
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_SECONDS=1800
REFRESH_TOKEN_EXPIRE_SECONDS=604800

# 超级管理员（seed 时用）
SUPERUSER_USERNAME=admin
SUPERUSER_PASSWORD=admin@123
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_PHONE=13800000000

# 日志（可选）
# APP_LOG_PATH=logs/app_{date}.log
```

3) 启动服务
```bash
uv run start.py
# 访问文档： http://localhost:8000/api/docs
```

---

### 数据库迁移（Aerich）
初始化与迁移：
```bash
# 初始化（注意 -t 指向 TORTOISE_ORM）
aerich init -t app.core.database.TORTOISE_ORM
aerich init-db

# 之后的模型变更
aerich migrate --name "change"
aerich upgrade
```

---

### 初始化脚本（内置角色/权限/超级管理员）
```bash
# 删除所有表（DROP CASCADE）
uv run init_db.py drop

# 清空所有表数据（保留表结构）
uv run init_db.py truncate

# 初始化：内置权限/角色/角色权限绑定 + 超级管理员
uv run init_db.py seed
```

---

### 统一响应
- 除登录外，所有 API 返回：
```json
{
  "code": 200,
  "message": "success",
  "data": { /* 业务数据 */ }
}
```
- 422 验证错误已做友好化：`message` 为首条可读提示，`data` 为精简错误列表（field/message/type）。

---

### 认证与权限
- 登录采用 OAuth2 表单：`POST /api/v1/auth/login` 返回 `access_token` 与 `refresh_token`
- 刷新：`POST /api/v1/auth/refresh`
- 注销：`POST /api/v1/auth/logout`（令牌版本自增，旧令牌失效）
- 权限常量集中于 `app/core/constants.py`，路由通过依赖 `has_permission(Permission.XXX)` 鉴权
- Redis 权限缓存：`rbac:perm:v{perm_version}:u:{user_id}`，变更后 `bump_perm_version()` 全量失效

---

### 审计日志
- 服务层操作使用 `@log_operation(action=...)` 记录：actor_id、action、target_id、path、method、ip、ua、status、latency_ms、trace_id、error
- 查询：`GET /api/v1/logs/`

---

### 核心 API（节选）
- 认证：
  - POST /api/v1/auth/login
  - POST /api/v1/auth/refresh
  - POST /api/v1/auth/logout
- 用户：
  - GET  /api/v1/users/me（自查，无需权限）
  - POST /api/v1/users/me/password（自助改密：旧密码/新密码/确认）
  - POST /api/v1/users/（创建）
  - PUT  /api/v1/users/{user_id}（乐观锁）
  - GET  /api/v1/users/{user_id}（详情）
  - GET  /api/v1/users/（分页）
  - POST /api/v1/users/disable（批量禁用）
  - POST /api/v1/users/bind-roles（单用户绑定角色）
  - POST /api/v1/users/bind-roles/batch（多用户批量绑定）
  - POST /api/v1/users/unbind-roles（单用户解绑）
  - POST /api/v1/users/unbind-roles/batch（多用户批量解绑）
  - POST /api/v1/users/{user_id}/password（管理员改密：新密码/确认）
- 角色：
  - POST /api/v1/roles/
  - PUT  /api/v1/roles/{role_id}
  - GET  /api/v1/roles/{role_id}
  - GET  /api/v1/roles/
  - POST /api/v1/roles/disable
  - POST /api/v1/roles/bind-permissions
  - POST /api/v1/roles/bind-permissions/batch
  - POST /api/v1/roles/unbind-permissions
  - POST /api/v1/roles/unbind-permissions/batch
  - GET  /api/v1/roles/{role_id}/users（查看角色下用户）
- 权限：
  - POST /api/v1/permissions/
  - PUT  /api/v1/permissions/{perm_id}
  - GET  /api/v1/permissions/{perm_id}
  - GET  /api/v1/permissions/
  - POST /api/v1/permissions/disable
  - GET  /api/v1/permissions/{perm_id}/roles（查看权限下角色）
- 日志：
  - GET  /api/v1/logs/

---

### 数据安全与性能
- 软删除：`is_deleted` + `deleted_at`
- 乐观锁：`version` 字段；DAO `update_with_version(id, version, data)`
- 批量操作：`bulk_create/update/soft_delete/restore/upsert`、关系批量绑定/解绑
- Redis：权限集合缓存与全局版本失效
- 日志：控制台 + 文件（按日期、10MB 轮转、15 天保留）；生产可开启 JSON 文件日志

---

### 开发与测试
- 运行测试
```bash
uv run pytest -v
```

---

### 许可
仅供学习与参考，可在此基础上继续二次开发定制。


