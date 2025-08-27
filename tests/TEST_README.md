# 测试指南

本项目包含了全面的API测试套件，覆盖了所有主要功能模块。

## 测试结构

```
tests/
├── __init__.py                 # 测试包初始化
├── conftest.py                 # 测试配置和fixture
├── test_auth.py               # 认证API测试
├── test_users.py              # 用户管理API测试
├── test_users_roles.py        # 用户角色绑定API测试
├── test_roles.py              # 角色管理API测试
├── test_roles_permissions.py  # 角色权限绑定API测试
├── test_permissions.py        # 权限管理API测试
├── test_logs.py               # 审计日志API测试
├── test_system.py             # 系统相关API测试
└── test_edge_cases.py         # 边界情况和错误处理测试
```

## 运行测试

### 基本用法

```bash
# 运行所有测试
uv run run_tests.py

# 或者直接使用pytest
pytest tests/ -v
```

### 高级用法

```bash
# 运行带覆盖率的测试
uv run run_tests.py coverage

# 快速测试（跳过慢测试）
uv run run_tests.py fast

# 运行特定测试文件
uv run run_tests.py tests/test_auth.py

# 运行特定测试类
uv run run_tests.py tests/test_users.py::TestUsers

# 运行特定测试方法
uv run run_tests.py tests/test_auth.py::TestAuth::test_login_success
```

## 测试数据

测试使用以下预置数据：

- **管理员账户**: username=`admin`, password=`admin@123`
- **测试数据库**: SQLite内存数据库
- **测试Redis**: redis://localhost:6379/15

## 测试覆盖

### 认证模块 (test_auth.py)
- ✅ 登录成功/失败
- ✅ 刷新令牌
- ✅ 注销
- ✅ 各种认证错误情况

### 用户管理 (test_users.py)
- ✅ 创建用户
- ✅ 获取用户信息
- ✅ 更新用户（乐观锁）
- ✅ 分页查询
- ✅ 禁用用户
- ✅ 密码管理
- ✅ 解锁用户

### 用户角色绑定 (test_users_roles.py)
- ✅ 绑定/解绑角色
- ✅ 批量绑定/解绑
- ✅ 权限验证

### 角色管理 (test_roles.py)
- ✅ 创建角色
- ✅ 更新角色（乐观锁）
- ✅ 删除角色（软删除/硬删除）
- ✅ 批量操作
- ✅ 查看角色用户

### 角色权限绑定 (test_roles_permissions.py)
- ✅ 绑定/解绑权限
- ✅ 批量绑定/解绑
- ✅ 权限验证

### 权限管理 (test_permissions.py)
- ✅ 创建权限
- ✅ 更新权限（乐观锁）
- ✅ 删除权限（软删除/硬删除）
- ✅ 批量操作
- ✅ 查看权限角色

### 审计日志 (test_logs.py)
- ✅ 查询操作日志
- ✅ 按条件过滤
- ✅ 个人操作记录
- ✅ 分页功能

### 系统接口 (test_system.py)
- ✅ 健康检查
- ✅ 指标接口
- ✅ API文档
- ✅ CORS测试

### 边界情况 (test_edge_cases.py)
- ✅ 输入验证
- ✅ 错误处理
- ✅ 并发控制
- ✅ 安全测试（SQL注入、XSS等）

## 测试环境要求

1. **uv run 3.13+**
2. **Redis服务** (用于缓存测试)
3. **测试依赖**:
   ```bash
   uv add pytest pytest-asyncio pytest-cov
   ```

## 测试最佳实践

1. **独立性**: 每个测试都是独立的，不依赖其他测试的结果
2. **清理**: 使用内存数据库，每次测试后自动清理
3. **数据隔离**: 测试数据使用唯一标识符，避免冲突
4. **覆盖率**: 目标覆盖率 >90%
5. **性能**: 测试运行时间 <30秒

## 问题排查

### 常见问题

1. **Redis连接失败**
   ```bash
   # 确保Redis服务运行
   redis-server
   ```

2. **权限错误**
   ```bash
   # 检查admin用户是否正确创建
   uv run -c "from tests.conftest import _seed_builtin; import asyncio; asyncio.run(_seed_builtin())"
   ```

3. **测试数据冲突**
   ```bash
   # 清理测试缓存
   rm -rf .pytest_cache __pycache__ tests/__pycache__
   ```
