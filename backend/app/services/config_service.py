"""
Configuration service for managing global settings.
Handles default configuration initialization and CRUD operations.
"""
import json
from typing import Any, Optional, Dict, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import GlobalConfig


# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "default_provider": "local-llama",
    "default_model": "qwen3.6:27b",
    "default_temperature": 0.7,
    "default_max_tokens": 4096,
    "default_system_prompt": "You are a helpful assistant.",
    "db_query_allowed_tables": ["sessions", "messages", "tool_calls"],
    "web_search_timeout_seconds": 30,
    "web_search_max_results": 5,
    "db_query_timeout_seconds": 10,
    "db_query_max_rows": 100,
}


class ConfigService:
    """Service for managing global configuration."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the config service.

        Args:
            db: AsyncSession for database operations.
        """
        self.db = db

    async def get(self, key: str) -> Optional[Any]:
        """
        Get a configuration value by key.

        Args:
            key: The configuration key.

        Returns:
            The configuration value, or None if not found.
        """
        result = await self.db.execute(
            select(GlobalConfig).where(GlobalConfig.key == key)
        )
        config = result.scalar_one_or_none()
        return config.value if config else None

    async def get_all(self) -> Dict[str, Any]:
        """
        Get all configuration values.

        Returns:
            Dictionary of all configuration key-value pairs.
        """
        result = await self.db.execute(select(GlobalConfig))
        configs = result.scalars().all()
        return {config.key: config.value for config in configs}

    async def set(self, key: str, value: Any) -> GlobalConfig:
        """
        Set a configuration value.

        Args:
            key: The configuration key.
            value: The configuration value (will be stored as JSON).

        Returns:
            The created or updated GlobalConfig object.
        """
        result = await self.db.execute(
            select(GlobalConfig).where(GlobalConfig.key == key)
        )
        config = result.scalar_one_or_none()

        if config:
            config.value = value
            config.updated_at = datetime.utcnow()
        else:
            config = GlobalConfig(key=key, value=value)
            self.db.add(config)

        await self.db.flush()
        return config

    async def delete(self, key: str) -> bool:
        """
        Delete a configuration key.

        Args:
            key: The configuration key to delete.

        Returns:
            True if deleted, False if not found.
        """
        result = await self.db.execute(
            select(GlobalConfig).where(GlobalConfig.key == key)
        )
        config = result.scalar_one_or_none()

        if config:
            await self.db.delete(config)
            await self.db.flush()
            return True
        return False

    async def initialize_defaults(self) -> Dict[str, Any]:
        """
        Initialize default configuration values.
        Only sets values that don't already exist.

        Returns:
            Dictionary of all configuration values after initialization.
        """
        for key, value in DEFAULT_CONFIG.items():
            existing = await self.get(key)
            if existing is None:
                await self.set(key, value)

        await self.db.flush()
        return await self.get_all()

    async def get_with_default(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with a default fallback.

        Args:
            key: The configuration key.
            default: Default value if key not found.

        Returns:
            The configuration value or the default.
        """
        value = await self.get(key)
        if value is not None:
            return value
        return DEFAULT_CONFIG.get(key, default)

    # Convenience methods for specific configurations

    async def get_default_provider(self) -> str:
        """Get the default provider ID."""
        return await self.get_with_default("default_provider", "local-llama")

    async def get_default_model(self) -> str:
        """Get the default model name."""
        return await self.get_with_default("default_model", "qwen3.6:27b")

    async def get_default_temperature(self) -> float:
        """Get the default temperature."""
        return float(await self.get_with_default("default_temperature", 0.7))

    async def get_default_max_tokens(self) -> int:
        """Get the default max tokens."""
        return int(await self.get_with_default("default_max_tokens", 4096))

    async def get_default_system_prompt(self) -> str:
        """Get the default system prompt."""
        return await self.get_with_default(
            "default_system_prompt",
            "You are a helpful assistant."
        )

    async def get_db_query_allowed_tables(self) -> List[str]:
        """Get the list of allowed tables for db_query tool."""
        return await self.get_with_default(
            "db_query_allowed_tables",
            ["sessions", "messages", "tool_calls"]
        )

    async def get_web_search_config(self) -> Dict[str, Any]:
        """Get web_search tool configuration."""
        return {
            "timeout_seconds": await self.get_with_default("web_search_timeout_seconds", 30),
            "max_results": await self.get_with_default("web_search_max_results", 5),
        }

    async def get_db_query_config(self) -> Dict[str, Any]:
        """Get db_query tool configuration."""
        return {
            "timeout_seconds": await self.get_with_default("db_query_timeout_seconds", 10),
            "max_rows": await self.get_with_default("db_query_max_rows", 100),
            "allowed_tables": await self.get_db_query_allowed_tables(),
        }
