"""
Custom Provider implementation.

Provides integration with custom OpenAI-compatible endpoints.
Supports any API that follows the OpenAI chat completion format.
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


class CustomProvider(BaseOpenAICompatibleProvider):
    """
    Provider for custom OpenAI-compatible endpoints.

    This provider allows connecting to any API that implements
    OpenAI's chat completion format, including:
    - Local model servers (vLLM, text-generation-webui, etc.)
    - Third-party API providers (Together, Anyscale, etc.)
    - Self-hosted model deployments
    - Azure OpenAI

    Configuration:
    - endpoint: Required - The base URL for the API
    - api_key: Optional - API key if required by the endpoint
    - config: Additional settings like model aliases, capabilities
    """

    @property
    def provider_type(self) -> str:
        """Return the provider type identifier."""
        return "custom"

    @property
    def base_url(self) -> str:
        """
        Return the base URL for the custom endpoint.

        Raises:
            ProviderError: If no endpoint is configured.
        """
        if not self.config.endpoint:
            raise ProviderError(
                "Custom provider requires an endpoint URL",
                self.provider_id
            )

        url = self.config.endpoint.rstrip("/")

        # Check if endpoint already contains the full chat path
        if url.endswith("/chat/completions"):
            # Already complete URL - extract base for client
            return url.rsplit("/chat/completions", 1)[0]

        return url

    @property
    def chat_path(self) -> str:
        """
        Return the path for chat completion endpoint.

        Smart path handling:
        - If endpoint ends with /chat/completions, use empty path (handled in base_url)
        - Otherwise, use /chat/completions
        """
        if not self.config.endpoint:
            return "/chat/completions"

        url = self.config.endpoint.rstrip("/")

        # If endpoint already contains the full path, use empty string
        if url.endswith("/chat/completions"):
            return "/chat/completions"  # Will be appended to base_url (which has path stripped)

        # Otherwise, use standard path
        return "/chat/completions"

    @property
    def default_headers(self) -> Dict[str, str]:
        """
        Return default headers for the custom endpoint.

        Includes Authorization header if API key is provided.
        Some custom endpoints may not require authentication.
        """
        headers = {
            "Content-Type": "application/json",
        }

        # Add authorization if API key is provided
        if self.config.api_key:
            # Check for custom auth header format
            auth_format = self.config.config.get("auth_format", "bearer")

            if auth_format == "bearer":
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            elif auth_format == "api_key":
                headers["X-API-Key"] = self.config.api_key
            elif auth_format == "custom":
                # Use custom header name from config
                header_name = self.config.config.get("auth_header", "Authorization")
                headers[header_name] = self.config.api_key

        # Add any custom headers from config
        custom_headers = self.config.config.get("headers", {})
        headers.update(custom_headers)

        return headers

    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available models from the custom endpoint.

        If the endpoint doesn't support /v1/models, returns configured
        models or a default model entry.

        Returns:
            List of ModelInfo objects.
        """
        # Try API endpoint first
        try:
            models = await super().list_models()
            if models:
                # Apply configured capabilities
                for model in models:
                    self._enhance_model_info(model)
                return models
        except ProviderError:
            pass
        except Exception:
            pass

        # Fallback: use configured models
        configured_models = self.config.config.get("models", [])

        if configured_models:
            return [
                self._create_model_info(m)
                for m in configured_models
            ]

        # Final fallback: default model
        default_model = self.config.config.get("default_model", "default")
        return [
            ModelInfo(
                id=default_model,
                name=f"Custom Model ({default_model})",
                provider=self.provider_type,
                supports_tools=self.config.config.get("supports_tools", True),
                supports_vision=self.config.config.get("supports_vision", False),
                metadata={
                    "endpoint": self.config.endpoint,
                }
            )
        ]

    def _enhance_model_info(self, model: ModelInfo) -> None:
        """
        Enhance model info with configured capabilities.

        Args:
            model: ModelInfo to enhance (modified in place).
        """
        model.provider = self.provider_type

        # Check for model-specific config
        model_configs = self.config.config.get("model_configs", {})
        model_config = model_configs.get(model.id, {})

        if "supports_tools" in model_config:
            model.supports_tools = model_config["supports_tools"]
        elif "supports_tools" in self.config.config:
            model.supports_tools = self.config.config["supports_tools"]

        if "supports_vision" in model_config:
            model.supports_vision = model_config["supports_vision"]
        elif "supports_vision" in self.config.config:
            model.supports_vision = self.config.config["supports_vision"]

        if "context_length" in model_config:
            model.context_length = model_config["context_length"]

    def _create_model_info(self, model_config: Dict[str, Any]) -> ModelInfo:
        """
        Create ModelInfo from a configuration dictionary.

        Args:
            model_config: Model configuration dictionary.

        Returns:
            ModelInfo object.
        """
        model_id = model_config.get("id", "unknown")

        return ModelInfo(
            id=model_id,
            name=model_config.get("name", model_id),
            provider=self.provider_type,
            owned_by=model_config.get("owned_by"),
            context_length=model_config.get("context_length"),
            supports_tools=model_config.get("supports_tools", True),
            supports_vision=model_config.get("supports_vision", False),
            metadata={
                "endpoint": self.config.endpoint,
                **model_config.get("metadata", {}),
            }
        )

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
        Send a chat completion request to the custom endpoint.

        Handles provider-specific parameter adjustments.
        """
        # Check if tools are supported for this model
        if tools:
            supports_tools = self._check_tool_support(model)
            if not supports_tools:
                tools = None
                tool_choice = None

        # Apply any parameter transformations from config
        params = self._transform_params(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        return await super().chat(**params)

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
        Send a streaming chat completion request to the custom endpoint.
        """
        # Check if tools are supported
        if tools:
            supports_tools = self._check_tool_support(model)
            if not supports_tools:
                tools = None
                tool_choice = None

        params = self._transform_params(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            tool_choice=tool_choice,
            **kwargs
        )

        async for chunk in super().chat_stream(**params):
            yield chunk

    def _check_tool_support(self, model: str) -> bool:
        """
        Check if a model supports function calling.

        Args:
            model: Model identifier.

        Returns:
            True if tools are supported.
        """
        # Check model-specific config
        model_configs = self.config.config.get("model_configs", {})
        if model in model_configs:
            return model_configs[model].get("supports_tools", True)

        # Check global config
        return self.config.config.get("supports_tools", True)

    def _transform_params(self, **params: Any) -> Dict[str, Any]:
        """
        Transform parameters based on provider configuration.

        Some custom endpoints may require parameter renaming or
        format changes.

        Args:
            **params: Original parameters.

        Returns:
            Transformed parameters dictionary.
        """
        # Get parameter mappings from config
        param_mappings = self.config.config.get("param_mappings", {})

        transformed = {}
        for key, value in params.items():
            # Apply mapping if defined
            mapped_key = param_mappings.get(key, key)
            transformed[mapped_key] = value

        return transformed

    async def validate_connection(self) -> bool:
        """
        Validate connection to the custom endpoint.

        Returns:
            True if the endpoint is reachable and properly configured.
        """
        if not self.config.endpoint:
            return False

        try:
            await self.list_models()
            return True
        except ProviderError:
            # Endpoint might not support /v1/models but still be valid
            # Try a minimal request if configured
            if self.config.config.get("skip_model_list"):
                return True
            return False
        except Exception:
            return False
