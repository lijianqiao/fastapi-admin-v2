"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: system_config.py
@DateTime: 2025/08/27 15:20:00
@Docs: 系统配置（可运行时修改，覆盖 .env 默认值）
"""

from tortoise import fields

from app.models.base import BaseModel


class SystemConfig(BaseModel):
    """系统配置单例表。

    说明：
    - 仅维护一条记录（由 Service 保证 get_or_create(id=1)）。
    - 字段若为 None/0 则表示使用 .env 默认或不启用。
    """

    # 项目信息
    project_name = fields.CharField(max_length=128, null=True, description="项目名称")
    project_description = fields.CharField(max_length=255, null=True, description="项目描述")
    project_url = fields.CharField(max_length=255, null=True, description="项目URL")

    # 分页
    default_page_size = fields.IntField(default=20, description="默认分页大小")

    # 密码策略
    password_min_length = fields.IntField(default=6, description="最小密码长度")
    password_require_uppercase = fields.BooleanField(default=False, description="必须包含大写字母")
    password_require_lowercase = fields.BooleanField(default=False, description="必须包含小写字母")
    password_require_digits = fields.BooleanField(default=False, description="必须包含数字")
    password_require_special = fields.BooleanField(default=False, description="必须包含特殊字符")
    password_expire_days = fields.IntField(default=0, description="密码有效期（天），0 表示永不过期")

    # 登录安全
    login_max_failed_attempts = fields.IntField(default=5, description="最大登录尝试次数")
    login_lock_minutes = fields.IntField(default=3, description="账户锁定时间（分钟）")
    session_timeout_hours = fields.IntField(default=0, description="会话超时时间（小时），0 使用 .env")
    force_https = fields.BooleanField(default=False, description="是否强制使用 HTTPS")

    class Meta:  # type: ignore
        table = "system_config"
        indexes = (("updated_at",),)


__all__ = ["SystemConfig"]
