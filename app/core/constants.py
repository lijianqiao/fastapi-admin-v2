"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: constants.py
@DateTime: 2025/08/21 10:06:11
@Docs: 常量定义
"""

from enum import StrEnum


class Permission(StrEnum):
    """权限常量（内嵌标题与描述，消除双处维护）。

    使用说明：
    - 每个枚举成员的 ``value`` 仍为权限字符串（用于存库/校验/比较）。
    - 额外携带 ``title`` 与 ``description``，用于初始化与展示。
    - 兼容仅传入字符串的旧写法；未显式提供时，``title/description`` 默认等于 ``value``。
    """

    # 为静态类型检查器声明动态添加的属性
    title: str  # type: ignore[override]  # 避免与 str.title 方法签名冲突的检查
    description: str

    def __new__(cls, value: str, title: str | None = None, description: str | None = None) -> "Permission":  # type: ignore[override]
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.title = title or value
        obj.description = description or value
        return obj

    USER_LIST = ("user:list", "用户列表", "查看用户列表")
    USER_CREATE = ("user:create", "创建用户", "创建新用户")
    USER_UPDATE = ("user:update", "更新用户", "更新用户信息")
    USER_DELETE = ("user:delete", "删除用户", "删除用户")
    USER_HARD_DELETE = ("user:hard_delete", "硬删除用户", "硬删除用户")
    USER_BULK_DELETE = ("user:bulk_delete", "批量删除用户", "批量删除用户")
    USER_DISABLE = ("user:disable", "禁用用户", "禁用用户")
    USER_BIND_ROLES = ("user:bind_roles", "绑定角色", "绑定角色")
    USER_UNBIND_ROLES = ("user:unbind_roles", "解绑角色", "解绑角色")
    USER_BIND_ROLES_BATCH = ("user:bind_roles_batch", "批量绑定角色", "批量绑定角色")
    USER_UNBIND_ROLES_BATCH = ("user:unbind_roles_batch", "批量解绑角色", "批量解绑角色")
    USER_UNLOCK = ("user:unlock", "解锁用户", "解锁用户")

    ROLE_LIST = ("role:list", "角色列表", "查看角色列表")
    ROLE_CREATE = ("role:create", "创建角色", "创建新角色")
    ROLE_UPDATE = ("role:update", "更新角色", "更新角色信息")
    ROLE_DELETE = ("role:delete", "删除角色", "删除角色")
    ROLE_HARD_DELETE = ("role:hard_delete", "硬删除角色", "硬删除角色")
    ROLE_BULK_DELETE = ("role:bulk_delete", "批量删除角色", "批量删除角色")
    ROLE_DISABLE = ("role:disable", "禁用角色", "禁用角色")
    ROLE_BIND_PERMISSIONS = ("role:bind_permissions", "绑定权限", "绑定权限")
    ROLE_UNBIND_PERMISSIONS = ("role:unbind_permissions", "解绑权限", "解绑权限")
    ROLE_BIND_PERMISSIONS_BATCH = ("role:bind_permissions_batch", "批量绑定权限", "批量绑定权限")
    ROLE_UNBIND_PERMISSIONS_BATCH = ("role:unbind_permissions_batch", "批量解绑权限", "批量解绑权限")

    PERMISSION_LIST = ("permission:list", "权限列表", "查看权限列表")
    PERMISSION_CREATE = ("permission:create", "创建权限", "创建权限")
    PERMISSION_UPDATE = ("permission:update", "更新权限", "更新权限")
    PERMISSION_DELETE = ("permission:delete", "删除权限", "删除权限")
    PERMISSION_HARD_DELETE = ("permission:hard_delete", "硬删除权限", "硬删除权限")
    PERMISSION_BULK_DELETE = ("permission:bulk_delete", "批量删除权限", "批量删除权限")
    PERMISSION_DISABLE = ("permission:disable", "禁用权限", "禁用权限")

    LOG_LIST = ("log:list", "审计日志列表", "查看审计日志")
    LOG_SELF = ("log:self", "我的操作记录", "查看我的操作记录")

    # 扩展列表（含软删/禁用/活跃）
    USER_LIST_ALL = ("user:list_all", "所有用户列表", "查看所有用户列表")
    ROLE_LIST_ALL = ("role:list_all", "所有角色列表", "查看所有角色列表")
    PERMISSION_LIST_ALL = ("permission:list_all", "所有权限列表", "查看所有权限列表")

    # 系统配置
    SYSTEM_CONFIG_READ = ("system:config:read", "系统配置读取", "读取系统配置")
    SYSTEM_CONFIG_UPDATE = ("system:config:update", "系统配置更新", "更新系统配置")


__all__ = ["Permission"]
