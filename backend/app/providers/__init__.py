"""
Model Provider module.

This module provides the core abstraction for LLM providers,
including the ModelProvider protocol and provider implementations.
"""
from app.providers.base import (
    ModelProvider,
    ModelInfo,
    ProviderConfig,
    ChatMessage,
    ToolCall,
    ToolResult,
    ChatCompletionResult,
    ProviderError,
    ProviderNotFoundError,
    ModelNotFoundError,
)
from app.providers.factory import (
    ProviderFactory,
    get_provider_factory,
    create_provider,
    register_provider,
)
from app.providers.llama_cpp import LlamaCppProvider
from app.providers.openai import OpenAIProvider
from app.providers.custom import CustomProvider

__all__ = [
    # Protocol and base types
    "ModelProvider",
    "ModelInfo",
    "ProviderConfig",
    "ChatMessage",
    "ToolCall",
    "ToolResult",
    "ChatCompletionResult",
    # Exceptions
    "ProviderError",
    "ProviderNotFoundError",
    "ModelNotFoundError",
    # Factory
    "ProviderFactory",
    "get_provider_factory",
    "create_provider",
    "register_provider",
    # Provider implementations
    "LlamaCppProvider",
    "OpenAIProvider",
    "CustomProvider",
]
