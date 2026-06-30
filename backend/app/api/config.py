"""
Global configuration API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import ConfigService
from app.schemas.api import GlobalConfigUpdate, GlobalConfigResponse

router = APIRouter(prefix="/config", tags=["config"])


def get_config_service(db: AsyncSession = Depends(get_db)) -> ConfigService:
    """Dependency for config service."""
    return ConfigService(db)


@router.get("", response_model=GlobalConfigResponse)
async def get_global_config(
    service: ConfigService = Depends(get_config_service)
):
    """
    Get global configuration.

    Returns all configuration values including:
    - Default provider and model
    - Default parameters (temperature, max_tokens)
    - Default system prompt
    - Tool configurations
    """
    config = await service.get_all()
    return GlobalConfigResponse(
        default_provider=config.get("default_provider"),
        default_model=config.get("default_model"),
        default_temperature=config.get("default_temperature"),
        default_max_tokens=config.get("default_max_tokens"),
        default_system_prompt=config.get("default_system_prompt"),
        db_query_allowed_tables=config.get("db_query_allowed_tables"),
        web_search_timeout_seconds=config.get("web_search_timeout_seconds"),
        web_search_max_results=config.get("web_search_max_results"),
        db_query_timeout_seconds=config.get("db_query_timeout_seconds"),
        db_query_max_rows=config.get("db_query_max_rows"),
    )


@router.put("", response_model=GlobalConfigResponse)
@router.patch("", response_model=GlobalConfigResponse)
async def update_global_config(
    data: GlobalConfigUpdate,
    service: ConfigService = Depends(get_config_service)
):
    """
    Update global configuration.

    Only provided fields will be updated.
    Changes affect new sessions by default.
    """
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        await service.set(key, value)

    # Return updated config
    config = await service.get_all()
    return GlobalConfigResponse(
        default_provider=config.get("default_provider"),
        default_model=config.get("default_model"),
        default_temperature=config.get("default_temperature"),
        default_max_tokens=config.get("default_max_tokens"),
        default_system_prompt=config.get("default_system_prompt"),
        db_query_allowed_tables=config.get("db_query_allowed_tables"),
        web_search_timeout_seconds=config.get("web_search_timeout_seconds"),
        web_search_max_results=config.get("web_search_max_results"),
        db_query_timeout_seconds=config.get("db_query_timeout_seconds"),
        db_query_max_rows=config.get("db_query_max_rows"),
    )


@router.post("/reset", response_model=GlobalConfigResponse)
async def reset_global_config(
    service: ConfigService = Depends(get_config_service)
):
    """
    Reset global configuration to defaults.

    All custom settings will be lost.
    """
    # Delete all existing config
    all_config = await service.get_all()
    for key in all_config.keys():
        await service.delete(key)

    # Reinitialize defaults
    await service.initialize_defaults()

    # Return reset config
    config = await service.get_all()
    return GlobalConfigResponse(
        default_provider=config.get("default_provider"),
        default_model=config.get("default_model"),
        default_temperature=config.get("default_temperature"),
        default_max_tokens=config.get("default_max_tokens"),
        default_system_prompt=config.get("default_system_prompt"),
        db_query_allowed_tables=config.get("db_query_allowed_tables"),
        web_search_timeout_seconds=config.get("web_search_timeout_seconds"),
        web_search_max_results=config.get("web_search_max_results"),
        db_query_timeout_seconds=config.get("db_query_timeout_seconds"),
        db_query_max_rows=config.get("db_query_max_rows"),
    )
