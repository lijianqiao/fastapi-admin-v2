"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: system_config.py
@DateTime: 2025/08/27 15:24:00
@Docs: 系统配置 Schemas
"""

from pydantic import BaseModel, Field, model_validator


class ProjectSettings(BaseModel):
    """项目设置"""

    name: str | None = Field(default=None, description="项目名称")
    description: str | None = Field(default=None, description="项目描述")
    url: str | None = Field(default=None, description="项目URL")


class PaginationSettings(BaseModel):
    """分页设置"""

    page_size: int = Field(default=20, ge=1, le=200, description="默认分页大小")


class PasswordPolicySettings(BaseModel):
    """密码策略设置"""

    min_length: int = Field(default=6, ge=4, le=128, description="最小密码长度")
    require_uppercase: bool = Field(default=False, description="必须包含大写字母")
    require_lowercase: bool = Field(default=False, description="必须包含小写字母")
    require_digits: bool = Field(default=False, description="必须包含数字")
    require_special: bool = Field(default=False, description="必须包含特殊字符")
    expire_days: int = Field(default=0, ge=0, le=3650, description="密码有效期（天），0 表示永不过期")

    @model_validator(mode="after")
    def _validate_ranges(self) -> "PasswordPolicySettings":
        # 如果四项全为 False，允许通过，表示仅长度限制
        return self


class LoginSecuritySettings(BaseModel):
    """登录安全设置"""

    max_failed_attempts: int = Field(default=5, ge=1, le=20)
    lock_minutes: int = Field(default=3, ge=1, le=1440)
    session_timeout_hours: int = Field(default=0, ge=0, le=168)
    force_https: bool = Field(default=False)


class SystemConfigOut(BaseModel):
    """系统配置输出"""

    version: int = Field(default=0, ge=0, description="当前配置版本（乐观锁）")
    project: ProjectSettings
    pagination: PaginationSettings
    password_policy: PasswordPolicySettings
    login_security: LoginSecuritySettings


class SystemConfigUpdateIn(BaseModel):
    """系统配置更新输入"""

    version: int = Field(..., ge=0, description="期望的当前版本（乐观锁）")
    project: ProjectSettings | None = None
    pagination: PaginationSettings | None = None
    password_policy: PasswordPolicySettings | None = None
    login_security: LoginSecuritySettings | None = None
