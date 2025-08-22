"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: init_db.py
@DateTime: 2025/08/21 13:22:00
@Docs: 数据库初始化脚本：重建/清空/初始化内置RBAC与超级管理员
"""

from __future__ import annotations

import argparse
import asyncio
from typing import Literal

from tortoise import Tortoise

from app.core.config import get_settings
from app.core.database import TORTOISE_ORM
from app.core.permissions import bump_perm_version
from app.core.security import hash_password
from app.models import Permission, Role, RolePermission, User, UserRole
from app.utils.builtin_rbac import get_builtin_permissions, get_builtin_roles, get_role_permission_map
from app.utils.logger import logger, setup_logger


async def drop_all() -> None:
    """删除所有表。"""
    logger.info("开始删除所有表（DROP CASCADE）...")
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    # 注意：PostgreSQL 使用 CASCADE
    await conn.execute_script(
        """
        DO $$ DECLARE r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        """
    )
    await Tortoise.close_connections()
    logger.info("已删除所有表。")


async def truncate_all() -> None:
    """清空所有表数据（不删除表）。"""
    logger.info("开始清空所有表数据（TRUNCATE ... RESTART IDENTITY CASCADE）...")
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    tables = [
        "user_roles",
        "role_permissions",
        "audit_logs",
        "permissions",
        "roles",
        "users",
    ]
    for tb in tables:
        await conn.execute_query(f'TRUNCATE TABLE "{tb}" RESTART IDENTITY CASCADE;')
    await Tortoise.close_connections()
    logger.info("已清空所有表数据。")


async def seed_builtin() -> None:
    """初始化内置角色与权限并创建超级管理员。"""
    logger.info("开始初始化内置权限、角色与超级管理员...")
    await Tortoise.init(config=TORTOISE_ORM)
    # 权限
    perm_map: dict[str, int] = {}
    perms_created = 0
    for p in get_builtin_permissions():
        perm_obj, created = await Permission.get_or_create(
            code=p["code"],
            defaults={
                "name": p["name"],
                "description": p["description"],
            },
        )
        perm_map[perm_obj.code] = int(perm_obj.id)
        if created:
            perms_created += 1

    # 角色
    role_map: dict[str, int] = {}
    roles_created = 0
    for r in get_builtin_roles():
        role_obj, created = await Role.get_or_create(
            code=r["code"],
            defaults={
                "name": r["name"],
                "description": r["description"],
            },
        )
        role_map[role_obj.code] = int(role_obj.id)
        if created:
            roles_created += 1

    # 绑定角色权限
    rp_map = get_role_permission_map()
    rp_bound = 0
    for role_code, perm_codes in rp_map.items():
        rid = role_map.get(role_code)
        if not rid:
            continue
        for code in perm_codes:
            pid = perm_map.get(code)
            if pid:
                _, created = await RolePermission.get_or_create(role_id=rid, permission_id=pid)
                if created:
                    rp_bound += 1

    # 超级管理员
    settings = get_settings()
    user, su_created = await User.get_or_create(
        username=settings.SUPERUSER_USERNAME,
        defaults={
            "phone": settings.SUPERUSER_PHONE,
            "email": settings.SUPERUSER_EMAIL,
            "password_hash": hash_password(settings.SUPERUSER_PASSWORD),
        },
    )
    super_role_id = role_map.get("super_admin")
    if super_role_id:
        _, ur_created = await UserRole.get_or_create(user_id=int(user.id), role_id=super_role_id)
    else:
        ur_created = False
    # 重建基础 RBAC 数据后，提升权限缓存的全局版本，强制失效旧缓存
    try:
        new_ver = await bump_perm_version()
        logger.info("已提升权限缓存版本：version={ver}", ver=new_ver)
    except Exception as _exc:
        logger.warning("提升权限缓存版本失败：{err}", err=str(_exc))

    await Tortoise.close_connections()
    logger.info(
        "初始化完成：新增权限={perms_created}，新增角色={roles_created}，新增角色-权限绑定={rp_bound}，超级管理员创建={su_created}，绑定超管角色={ur_created}",
        perms_created=perms_created,
        roles_created=roles_created,
        rp_bound=rp_bound,
        su_created=su_created,
        ur_created=ur_created,
    )


async def main_async(op: Literal["drop", "truncate", "seed"]) -> None:
    if op == "drop":
        await drop_all()
    elif op == "truncate":
        await truncate_all()
    elif op == "seed":
        await seed_builtin()


def main() -> None:
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("op", choices=["drop", "truncate", "seed"], help="操作类型")
    args = parser.parse_args()
    # 初始化日志
    try:
        env = get_settings().ENVIRONMENT
    except Exception:
        env = "development"
    setup_logger(env)
    logger.info("执行数据库初始化：op={op}", op=args.op)
    try:
        asyncio.run(main_async(args.op))
        logger.info("操作完成：op={op}", op=args.op)
    except Exception as exc:  # noqa: BLE001
        logger.exception("操作失败：op={op}, error={err}", op=args.op, err=str(exc))
        raise


if __name__ == "__main__":
    main()
