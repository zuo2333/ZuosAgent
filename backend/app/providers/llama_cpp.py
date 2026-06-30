"""
LlamaCpp Provider implementation.

Provides integration with llama.cpp server (OpenAI-compatible API).
Default endpoint: http://localhost:8080
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


class LlamaCppProvider(BaseOpenAICompatibleProvider):
    """
    Provider for llama.cpp server.

    Uses OpenAI-compatible API endpoints provided by llama.cpp server.
    Default endpoint is http://localhost:8080.

    The llama.cpp server provides OpenAI-compatible endpoints:
    - POST /v1/chat/completions
    - GET /v1/models
    """

    DEFAULT_ENDPOINT = "http://localhost:8080"

    @property
    def provider_type(self) -> str:
        """Return the provider type identifier."""
        return "llama_cpp"

    @property
    def base_url(self) -> str:
        """Return the base URL for the llama.cpp server."""
        endpoint = self.config.endpoint
        if endpoint:
            # Ensure no trailing slash
            return endpoint.rstrip("/")
        return self.DEFAULT_ENDPOINT

    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available models from llama.cpp server.

        llama.cpp server typically returns a single model entry
        representing the currently loaded model.

        Returns:
            List containing the loaded model info.
        """
        # Try to get models from API first
        try:
            models = await super().list_models()
            if models:
                # Enhance model info with llama.cpp specific metadata
                for model in models:
                    model.supports_tools = self._check_tool_support(model.id)
                return models
        except ProviderError:
            pass

        # Fallback: return a default model entry based on config
        default_model = self.config.config.get("default_model", "local-model")
        return [
            ModelInfo(
                id=default_model,
                name=f"Llama.cpp Model ({default_model})",
                provider=self.provider_type,
                owned_by="local",
                context_length=self.config.config.get("context_length", 4096),
                supports_tools=self._check_tool_support(default_model),
                metadata={
                    "endpoint": self.base_url,
                    "loaded_model": default_model,
                }
            )
        ]

    def _check_tool_support(self, model_id: str) -> bool:
        """
        Check if the model supports function calling.

        Some llama.cpp models support function calling based on
        their training. This can be configured in provider config.

        Args:
            model_id: Model identifier.

        Returns:
            True if tools are supported, False otherwise.
        """
        # Check explicit configuration
        if "supports_tools" in self.config.config:
            return bool(self.config.config["supports_tools"])

        # Default to True for modern models
        # Users can configure this explicitly if needed
        return True

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
        Send a chat completion request to llama.cpp server.

        llama.cpp server supports most OpenAI parameters.
        Some parameters like frequency_penalty may have limited support.
        """
        # llama.cpp may have different default behaviors
        # Adjust parameters as needed

        # If tools are not supported, remove them
        if tools and not self._check_tool_support(model):
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
        Send a streaming chat completion request to llama.cpp server.
        """
        # If tools are not supported, remove them
        if tools and not self._check_tool_support(model):
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
        Validate connection to llama.cpp server.

        Attempts to connect to the health endpoint or models endpoint.
        llama.cpp server may not have a dedicated health endpoint,
        so we try /v1/models.

        Returns:
            True if the server is reachable, False otherwise.
        """
        try:
            # Try to get models as a connection test
            await self.list_models()
            return True
        except Exception:
            return False
