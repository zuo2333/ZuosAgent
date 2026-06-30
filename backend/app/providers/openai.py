"""
OpenAI Provider implementation.

Provides integration with OpenAI's API.
Supports GPT-4, GPT-3.5, and other OpenAI models.
"""
from typing import List, Dict, Any, Optional, AsyncIterator

from app.providers.base import (
    ModelInfo,
    ProviderConfig,
    ChatMessage,
    ChatCompletionResult,
    ProviderError,
)
from app.providers.openai_compatible import BaseOpenAICompatibleProvider


class OpenAIProvider(BaseOpenAICompatibleProvider):
    """
    Provider for OpenAI API.

    Supports all OpenAI models including GPT-4, GPT-3.5-turbo, etc.
    Requires an API key for authentication.

    Known model capabilities:
    - GPT-4 and GPT-4-turbo: Function calling, vision (turbo)
    - GPT-3.5-turbo: Function calling
    - GPT-4o: Function calling, vision
    """

    OPENAI_API_BASE = "https://api.openai.com/v1"

    # Known model information
    KNOWN_MODELS = {
        "gpt-4": {
            "name": "GPT-4",
            "context_length": 8192,
            "supports_tools": True,
            "supports_vision": False,
        },
        "gpt-4-32k": {
            "name": "GPT-4 32K",
            "context_length": 32768,
            "supports_tools": True,
            "supports_vision": False,
        },
        "gpt-4-turbo": {
            "name": "GPT-4 Turbo",
            "context_length": 128000,
            "supports_tools": True,
            "supports_vision": True,
        },
        "gpt-4-turbo-preview": {
            "name": "GPT-4 Turbo Preview",
            "context_length": 128000,
            "supports_tools": True,
            "supports_vision": False,
        },
        "gpt-4o": {
            "name": "GPT-4o",
            "context_length": 128000,
            "supports_tools": True,
            "supports_vision": True,
        },
        "gpt-4o-mini": {
            "name": "GPT-4o Mini",
            "context_length": 128000,
            "supports_tools": True,
            "supports_vision": True,
        },
        "gpt-3.5-turbo": {
            "name": "GPT-3.5 Turbo",
            "context_length": 16385,
            "supports_tools": True,
            "supports_vision": False,
        },
        "gpt-3.5-turbo-16k": {
            "name": "GPT-3.5 Turbo 16K",
            "context_length": 16385,
            "supports_tools": True,
            "supports_vision": False,
        },
        "o1": {
            "name": "o1",
            "context_length": 200000,
            "supports_tools": False,  # o1 doesn't support tools yet
            "supports_vision": True,
        },
        "o1-mini": {
            "name": "o1-mini",
            "context_length": 128000,
            "supports_tools": False,
            "supports_vision": False,
        },
        "o1-preview": {
            "name": "o1-preview",
            "context_length": 128000,
            "supports_tools": False,
            "supports_vision": False,
        },
    }

    @property
    def provider_type(self) -> str:
        """Return the provider type identifier."""
        return "openai"

    @property
    def base_url(self) -> str:
        """Return the base URL for OpenAI API."""
        # Allow custom endpoint for Azure OpenAI or proxies
        if self.config.endpoint:
            return self.config.endpoint.rstrip("/")
        return self.OPENAI_API_BASE

    @property
    def default_headers(self) -> Dict[str, str]:
        """Return default headers including API key."""
        headers = super().default_headers

        # OpenAI requires an API key
        if not self.config.api_key:
            raise ProviderError(
                "OpenAI API key is required",
                self.provider_id
            )

        return headers

    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available OpenAI models.

        Combines API response with known model information
        for enhanced metadata.

        Returns:
            List of ModelInfo objects for available models.
        """
        # Get models from API
        api_models = await super().list_models()

        # Enhance with known model information
        enhanced_models = []
        for model in api_models:
            model_id = model.id

            # Check if we have known info for this model (or a matching prefix)
            known_info = None
            for known_id, info in self.KNOWN_MODELS.items():
                if model_id == known_id or model_id.startswith(known_id):
                    known_info = info
                    break

            if known_info:
                enhanced_model = ModelInfo(
                    id=model_id,
                    name=known_info.get("name", model_id),
                    provider=self.provider_type,
                    owned_by=model.owned_by or "openai",
                    context_length=known_info.get("context_length"),
                    supports_tools=known_info.get("supports_tools", True),
                    supports_vision=known_info.get("supports_vision", False),
                    metadata=model.metadata,
                )
            else:
                # Unknown model, use API data
                enhanced_model = model
                enhanced_model.provider = self.provider_type

            enhanced_models.append(enhanced_model)

        return enhanced_models

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs: Any,
    ) -> ChatCompletionResult:
        """
        Send a chat completion request to OpenAI.

        Supports all OpenAI parameters including function calling.
        """
        # Check if model supports tools
        model_info = self.KNOWN_MODELS.get(model, {})
        if tools and not model_info.get("supports_tools", True):
            # Model doesn't support tools, remove them
            tools = None
            tool_choice = None

        return await super().chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[str] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Send a streaming chat completion request to OpenAI.
        """
        # Check if model supports tools
        model_info = self.KNOWN_MODELS.get(model, {})
        if tools and not model_info.get("supports_tools", True):
            tools = None
            tool_choice = None

        async for chunk in super().chat_stream(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        ):
            yield chunk

    async def validate_connection(self) -> bool:
        """
        Validate the OpenAI API connection and API key.

        Returns:
            True if connection is valid and API key works.
        """
        if not self.config.api_key:
            return False

        try:
            await self.list_models()
            return True
        except ProviderError:
            return False
