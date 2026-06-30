"""
Base implementation for providers using OpenAI-compatible API.

Provides common functionality for providers that use OpenAI-compatible
endpoints (OpenAI, llama.cpp server, custom endpoints).
"""
import json
import httpx
from typing import List, Dict, Any, Optional, AsyncIterator
from abc import ABC, abstractmethod

from app.providers.base import (
    ModelProvider,
    ModelInfo,
    ProviderConfig,
    ChatMessage,
    ToolCall,
    ChatCompletionResult,
    ProviderError,
)


class BaseOpenAICompatibleProvider(ABC):
    """
    Base class for providers using OpenAI-compatible APIs.

    This class implements the ModelProvider protocol for any provider
    that uses an OpenAI-compatible API endpoint.
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize the provider.

        Args:
            config: Provider configuration containing endpoint, API key, etc.
        """
        self.config = config
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider instance."""
        return self.config.provider_id

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """Type of provider."""
        ...

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL for the API endpoint."""
        ...

    @property
    def default_headers(self) -> Dict[str, str]:
        """Default headers for API requests."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return headers

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.default_headers,
                timeout=httpx.Timeout(300.0, connect=30.0),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    def _format_messages(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        Format messages for OpenAI API.

        Args:
            messages: List of ChatMessage objects.

        Returns:
            List of message dictionaries in OpenAI format.
        """
        formatted = []
        for msg in messages:
            message_dict = {
                "role": msg.role,
            }

            if msg.content is not None:
                message_dict["content"] = msg.content

            if msg.name:
                message_dict["name"] = msg.name

            if msg.tool_calls:
                message_dict["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in msg.tool_calls
                ]

            if msg.tool_call_id:
                message_dict["tool_call_id"] = msg.tool_call_id

            formatted.append(message_dict)

        return formatted

    @property
    def chat_path(self) -> str:
        """
        Return the path for chat completion endpoint.

        Subclasses can override this for different API paths.
        """
        return "/v1/chat/completions"

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
        Send a non-streaming chat completion request.
        """
        client = self._get_client()

        request_body: Dict[str, Any] = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "stream": False,
        }

        if max_tokens:
            request_body["max_tokens"] = max_tokens

        if tools:
            request_body["tools"] = tools
            if tool_choice:
                request_body["tool_choice"] = tool_choice

        # Add any additional parameters
        request_body.update(kwargs)

        try:
            response = await client.post(self.chat_path, json=request_body)
            response.raise_for_status()
            data = response.json()

            return self._parse_completion_response(data)

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except Exception:
                pass
            raise ProviderError(
                f"API request failed: {e.response.status_code} - {error_detail}",
                self.provider_id,
                e
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"Network error: {str(e)}",
                self.provider_id,
                e
            )
        except json.JSONDecodeError as e:
            raise ProviderError(
                f"Failed to parse API response: {str(e)}",
                self.provider_id,
                e
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
        Send a streaming chat completion request.

        Yields text chunks from the model response.
        """
        client = self._get_client()

        request_body: Dict[str, Any] = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "stream": True,
        }

        if max_tokens:
            request_body["max_tokens"] = max_tokens

        if tools:
            request_body["tools"] = tools
            if tool_choice:
                request_body["tool_choice"] = tool_choice

        request_body.update(kwargs)

        try:
            async with client.stream("POST", self.chat_path, json=request_body) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix

                        if data_str == "[DONE]":
                            break

                        try:
                            data = json.loads(data_str)
                            chunk = self._parse_stream_chunk(data)
                            if chunk:
                                yield chunk
                        except json.JSONDecodeError:
                            continue

        except httpx.HTTPStatusError as e:
            error_detail = ""
            try:
                error_detail = e.response.text
            except Exception:
                pass
            raise ProviderError(
                f"Streaming API request failed: {e.response.status_code} - {error_detail}",
                self.provider_id,
                e
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"Network error during streaming: {str(e)}",
                self.provider_id,
                e
            )

    def _parse_completion_response(self, data: Dict[str, Any]) -> ChatCompletionResult:
        """
        Parse a non-streaming completion response.

        Args:
            data: Raw API response data.

        Returns:
            ChatCompletionResult with content or tool_calls.
        """
        choices = data.get("choices", [])
        if not choices:
            return ChatCompletionResult(content="", finish_reason="empty")

        choice = choices[0]
        message = choice.get("message", {})
        finish_reason = choice.get("finish_reason")

        result = ChatCompletionResult(finish_reason=finish_reason)

        # Check for tool calls first
        if "tool_calls" in message and message["tool_calls"]:
            result.tool_calls = []
            for tc in message["tool_calls"]:
                result.tool_calls.append(ToolCall.from_openai(tc))
        else:
            result.content = message.get("content")

        # Parse usage if available
        if "usage" in data:
            result.usage = data["usage"]

        return result

    def _parse_stream_chunk(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Parse a streaming chunk and extract text content.

        Args:
            data: Raw chunk data.

        Returns:
            Text content from the chunk, or None if no content.
        """
        choices = data.get("choices", [])
        if not choices:
            return None

        delta = choices[0].get("delta", {})
        content = delta.get("content")

        return content if content else None

    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available models from the API.

        Returns:
            List of ModelInfo objects.
        """
        client = self._get_client()

        try:
            response = await client.get("/v1/models")
            response.raise_for_status()
            data = response.json()

            models = []
            for model_data in data.get("data", []):
                model = ModelInfo(
                    id=model_data.get("id", "unknown"),
                    name=model_data.get("id", "unknown"),
                    provider=self.provider_type,
                    owned_by=model_data.get("owned_by"),
                    metadata=model_data,
                )
                models.append(model)

            return models

        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"Failed to list models: {e.response.status_code}",
                self.provider_id,
                e
            )
        except httpx.RequestError as e:
            raise ProviderError(
                f"Network error while listing models: {str(e)}",
                self.provider_id,
                e
            )

    async def validate_connection(self) -> bool:
        """
        Validate that the provider is reachable.

        Returns:
            True if connection is valid, False otherwise.
        """
        try:
            await self.list_models()
            return True
        except ProviderError:
            return False
