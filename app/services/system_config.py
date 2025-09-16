"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: system_config.py
@DateTime: 2025/08/27 15:26:00
@Docs: 系统配置服务
"""

from app.core.config import get_settings
from app.dao.system_config import SystemConfigDAO
from app.schemas.system_config import (
    LoginSecuritySettings,
    PaginationSettings,
    PasswordPolicySettings,
    ProjectSettings,
    SystemConfigOut,
    SystemConfigUpdateIn,
)

_S = get_settings


class SystemConfigService:
    """系统配置服务"""

    def __init__(self, system_config_dao: SystemConfigDAO | None = None) -> None:
        self.dao = system_config_dao or SystemConfigDAO()

    async def get_config(self) -> SystemConfigOut:
        """获取系统配置

        Returns:
            SystemConfigOut: 系统配置
        """
        s = _S()
        m = await self.dao.get_singleton()
        project = ProjectSettings(
            name=m.project_name or s.APP_NAME,
            description=m.project_description or s.APP_DESCRIPTION,
            url=m.project_url or None,
        )
        pagination = PaginationSettings(page_size=m.default_page_size or 20)
        password_policy = PasswordPolicySettings(
            min_length=m.password_min_length or 8,
            require_uppercase=bool(getattr(m, "password_require_uppercase", False)),
            require_lowercase=bool(getattr(m, "password_require_lowercase", False)),
            require_digits=bool(getattr(m, "password_require_digits", False)),
            require_special=bool(getattr(m, "password_require_special", False)),
            expire_days=m.password_expire_days or 0,
        )
        login_security = LoginSecuritySettings(
            max_failed_attempts=m.login_max_failed_attempts or s.LOGIN_MAX_FAILED_ATTEMPTS,
            lock_minutes=m.login_lock_minutes or s.LOGIN_LOCK_MINUTES,
            session_timeout_hours=m.session_timeout_hours or 0,
            force_https=bool(m.force_https),
        )
        return SystemConfigOut(
            version=int(getattr(m, "version", 0) or 0),
            project=project,
            pagination=pagination,
            password_policy=password_policy,
            login_security=login_security,
        )

    async def update_config(self, payload: SystemConfigUpdateIn) -> SystemConfigOut:
        """更新系统配置

        Args:
            payload (SystemConfigUpdateIn): 更新数据

        Returns:
            SystemConfigOut: 更新后的系统配置
        """
        to_update: dict[str, object] = {}
        if payload.project is not None:
            if payload.project.name is not None:
                to_update["project_name"] = payload.project.name
            if payload.project.description is not None:
                to_update["project_description"] = payload.project.description
            if payload.project.url is not None:
                to_update["project_url"] = payload.project.url
        if payload.pagination is not None:
            to_update["default_page_size"] = payload.pagination.page_size
        if payload.password_policy is not None:
            to_update["password_min_length"] = payload.password_policy.min_length
            to_update["password_require_uppercase"] = payload.password_policy.require_uppercase
            to_update["password_require_lowercase"] = payload.password_policy.require_lowercase
            to_update["password_require_digits"] = payload.password_policy.require_digits
            to_update["password_require_special"] = payload.password_policy.require_special
            to_update["password_expire_days"] = payload.password_policy.expire_days
        if payload.login_security is not None:
            to_update["login_max_failed_attempts"] = payload.login_security.max_failed_attempts
            to_update["login_lock_minutes"] = payload.login_security.lock_minutes
            to_update["session_timeout_hours"] = payload.login_security.session_timeout_hours
            to_update["force_https"] = payload.login_security.force_https
        if to_update:
            # 使用 DAO 的并发安全更新方法
            m = await self.dao.get_singleton()
            if int(getattr(m, "version", 0) or 0) != int(payload.version):
                from app.core.exceptions import conflict

                raise conflict("配置已被其他人修改，请刷新后重试")
            await self.dao.update_partial(to_update)
        return await self.get_config()
