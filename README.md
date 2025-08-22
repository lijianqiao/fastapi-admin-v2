## FastAPI Admin RBAC

基于 FastAPI 的现代化 RBAC 权限管理系统，提供完整的用户、角色、权限管理和操作日志功能。

---

## 🚀 核心特性

- **RBAC 权限模型** - 用户-角色-权限三层权限控制
- **操作日志系统** - 自动记录用户操作行为
- **JWT 认证** - 安全的身份验证和授权
- **依赖注入权限控制** - 基于装饰器的细粒度权限检查
- **软删除支持** - 数据安全保护，支持恢复
- **高性能 DAO 层** - 支持批量操作、缓存优化
- **统一异常处理** - 标准化错误响应

---

## 🚀 技术栈
- Python 3.13、FastAPI、Pydantic v2、Loguru
- Tortoise-ORM、Aerich（迁移）、PostgreSQL + asyncpg
- Redis（权限缓存、令牌版本、限流）
- Prometheus Client（/metrics 指标暴露）
- phonenumbers（手机号校验）

---

## 📁 目录结构（核心）

```
- app/
  - api/v1/：各模块 REST API
  - core/：配置、数据库、异常、生命周期、权限工具等
  - models/：Tortoise 数据模型（含软删/乐观锁/索引）
  - dao/：DAO 层，封装 CRUD、批量、分页、关系操作
  - services/：服务层，业务编排与审计装饰器
  - schemas/：Pydantic 校验模型与统一响应模型
  - utils/：日志、Redis、审计装饰器、内置 RBAC 数据等
  - middlewares/：请求上下文、限流、指标采集
```
---

## ⚡快速开始
1) 安装依赖
```bash
# 创建环境
uv venv --python 3.13

# 安装依赖
uv sync

# 配置环境变量 (记得创建数据库，修改对应配置)
cp .env.example .env

# **初始化数据库**
aerich init -t app.core.database.TORTOISE_ORM
aerich init-db

# 初始化管理员用户、角色、权限 (环境变量文件可以修改初始化管理员账户的相关信息)
uv run init_db.py seed

# 删除所有表（DROP CASCADE） - 开发时期用
# uv run init_db.py drop

# 清空所有表数据（保留表结构） - 开发时期用
# uv run init_db.py truncate

# 运行应用
uv run start.py
```

#### Swagger Docs：http://127.0.0.1:8000/api/docs

---

## 许可
仅供学习与参考，可在此基础上继续二次开发定制。
