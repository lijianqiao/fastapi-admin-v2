"""
@Author: li
@Email: lijianqiao2906@live.com
@FileName: system.py
@DateTime: 2025/08/27 12:44:09
@Docs: 系统配置 API

提供系统运行时配置的读取与更新，覆盖 .env 默认值。
"""

from fastapi import APIRouter, Depends

from app.core.constants import Permission as Perm
from app.core.dependencies import get_system_config_service, has_permission
from app.schemas.response import Response
from app.schemas.system_config import SystemConfigOut, SystemConfigUpdateIn
from app.services.system_config import SystemConfigService

router = APIRouter()


@router.get(
    "/config",
    dependencies=[Depends(has_permission(Perm.SYSTEM_CONFIG_READ))],
    response_model=Response[SystemConfigOut],
    summary="获取系统配置",
)
async def get_config(svc: SystemConfigService = Depends(get_system_config_service)):
    """获取系统配置

    Args:
        svc (SystemConfigService): 系统配置服务

    Returns:
        Response[SystemConfigOut]: 系统配置响应
    """
    cfg = await svc.get_config()
    return Response[SystemConfigOut](data=cfg)


@router.put(
    "/config",
    dependencies=[Depends(has_permission(Perm.SYSTEM_CONFIG_UPDATE))],
    response_model=Response[SystemConfigOut],
    summary="更新系统配置",
)
async def update_config(payload: SystemConfigUpdateIn, svc: SystemConfigService = Depends(get_system_config_service)):
    """更新系统配置

    Args:
        payload (SystemConfigUpdateIn): 更新数据
        svc (SystemConfigService): 系统配置服务

    Returns:
        Response[SystemConfigOut]: 系统配置响应
    """
    cfg = await svc.update_config(payload)
    return Response[SystemConfigOut](data=cfg)
