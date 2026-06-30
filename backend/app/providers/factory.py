"""
Provider Factory module.

Implements the factory pattern for creating and managing provider instances.
Provides registration mechanism for extensible provider support.
"""
from typing import Dict, Type, Optional, Any, Callable
from functools import lru_cache

from app.providers.base import (
    ModelProvider,
    ProviderConfig,
    ProviderError,
    ProviderNotFoundError,
)
from app.providers.llama_cpp import LlamaCppProvider
from app.providers.openai import OpenAIProvider
from app.providers.custom import CustomProvider


class ProviderFactory:
    """
    Factory for creating and managing model provider instances.

    Supports registration of custom provider types and maintains
    a registry of available provider implementations.

    Usage:
        factory = ProviderFactory()

        # Register custom provider
        factory.register("my_provider", MyProvider)

        # Create provider instance
        provider = factory.create(config)

        # Get provider by type
        provider = factory.get_provider("openai", config)
    """

    # Registry of provider types to their implementations
    _registry: Dict[str, Type[ModelProvider]] = {}

    # Default provider implementations
    _default_providers: Dict[str, Type[ModelProvider]] = {
        "llama_cpp": LlamaCppProvider,
        "openai": OpenAIProvider,
        "custom": CustomProvider,
    }

    def __init__(self) -> None:
        """Initialize the factory with default providers."""
        # Copy default providers to registry
        if not self._registry:
            self._registry.update(self._default_providers)

    @classmethod
    def register(
        cls,
        provider_type: str,
        provider_class: Type[ModelProvider],
        overwrite: bool = False
    ) -> None:
        """
        Register a provider implementation.

        Args:
            provider_type: Unique identifier for the provider type.
            provider_class: The provider class to register.
            overwrite: If True, allow overwriting existing registration.

        Raises:
            ValueError: If provider_type already registered and overwrite=False.
        """
        if provider_type in cls._registry and not overwrite:
            raise ValueError(
                f"Provider type '{provider_type}' is already registered. "
                "Use overwrite=True to replace it."
            )
        cls._registry[provider_type] = provider_class

    @classmethod
    def unregister(cls, provider_type: str) -> bool:
        """
        Unregister a provider type.

        Args:
            provider_type: The provider type to unregister.

        Returns:
            True if the provider was unregistered, False if not found.
        """
        if provider_type in cls._registry:
            del cls._registry[provider_type]
            return True
        return False

    @classmethod
    def get_registered_types(cls) -> list[str]:
        """
        Get list of registered provider types.

        Returns:
            List of registered provider type identifiers.
        """
        return list(cls._registry.keys())

    def create(
        self,
        config: ProviderConfig,
        **kwargs: Any
    ) -> ModelProvider:
        """
        Create a provider instance based on configuration.

        Args:
            config: Provider configuration.
            **kwargs: Additional arguments passed to the provider constructor.

        Returns:
            Provider instance.

        Raises:
            ProviderNotFoundError: If provider type is not registered.
            ProviderError: If provider creation fails.
        """
        provider_type = config.provider_type

        if provider_type not in self._registry:
            raise ProviderNotFoundError(
                f"Provider type '{provider_type}' is not registered. "
                f"Available types: {list(self._registry.keys())}",
                config.provider_id
            )

        provider_class = self._registry[provider_type]

        try:
            return provider_class(config, **kwargs)
        except Exception as e:
            raise ProviderError(
                f"Failed to create provider '{config.provider_id}': {str(e)}",
                config.provider_id,
                e
            )

    def get_provider(
        self,
        provider_type: str,
        config: ProviderConfig,
        **kwargs: Any
    ) -> ModelProvider:
        """
        Get a provider instance by type.

        This is an alias for create() with explicit type validation.

        Args:
            provider_type: Type of provider to create.
            config: Provider configuration.
            **kwargs: Additional arguments.

        Returns:
            Provider instance.

        Raises:
            ProviderNotFoundError: If provider type is not registered.
        """
        if config.provider_type != provider_type:
            config = ProviderConfig(
                provider_id=config.provider_id,
                name=config.name,
                provider_type=provider_type,
                endpoint=config.endpoint,
                api_key=config.api_key,
                config=config.config,
                is_active=config.is_active,
            )

        return self.create(config, **kwargs)

    def is_registered(self, provider_type: str) -> bool:
        """
        Check if a provider type is registered.

        Args:
            provider_type: Provider type to check.

        Returns:
            True if registered, False otherwise.
        """
        return provider_type in self._registry


# Global factory instance
_factory_instance: Optional[ProviderFactory] = None


def get_provider_factory() -> ProviderFactory:
    """
    Get the global provider factory instance.

    Returns:
        Singleton ProviderFactory instance.
    """
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = ProviderFactory()
    return _factory_instance


def create_provider(config: ProviderConfig, **kwargs: Any) -> ModelProvider:
    """
    Convenience function to create a provider.

    Args:
        config: Provider configuration.
        **kwargs: Additional arguments for provider construction.

    Returns:
        Provider instance.
    """
    return get_provider_factory().create(config, **kwargs)


def register_provider(
    provider_type: str,
    provider_class: Type[ModelProvider],
    overwrite: bool = False
) -> None:
    """
    Convenience function to register a provider.

    Args:
        provider_type: Provider type identifier.
        provider_class: Provider class to register.
        overwrite: Allow overwriting existing registration.
    """
    ProviderFactory.register(provider_type, provider_class, overwrite)
