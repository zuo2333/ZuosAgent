"""
Base module for Model Provider abstraction.

Defines the ModelProvider protocol and common data structures
that all providers must implement.
"""
from typing import Protocol, AsyncIterator, List, Dict, Any, Optional, Literal, runtime_checkable
from dataclasses import dataclass, field
from pydantic import BaseModel
import uuid
from datetime import datetime


# ============================================================================
# Core Data Structures
# ============================================================================

class ChatMessage(BaseModel):
    """
    Chat message following OpenAI format.
    Used for communication between client and providers.
    """
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List["ToolCallData"]] = None
    tool_call_id: Optional[str] = None


class ToolCallData(BaseModel):
    """Tool call data structure."""
    id: str = field(default_factory=lambda: f"call_{uuid.uuid4().hex[:24]}")
    type: Literal["function"] = "function"
    function: "FunctionCallData"


class FunctionCallData(BaseModel):
    """Function call with name and arguments."""
    name: str
    arguments: str  # JSON string


# Rebuild models to resolve forward references
ChatMessage.model_rebuild()
ToolCallData.model_rebuild()


@dataclass
class ModelInfo:
    """
    Information about an available model.
    Returned by providers when listing available models.
    """
    id: str
    name: str
    provider: str
    owned_by: Optional[str] = None
    context_length: Optional[int] = None
    supports_tools: bool = True
    supports_vision: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider,
            "owned_by": self.owned_by,
            "context_length": self.context_length,
            "supports_tools": self.supports_tools,
            "supports_vision": self.supports_vision,
            "metadata": self.metadata,
        }


@dataclass
class ToolCall:
    """
    Tool call request from the model.
    """
    id: str
    name: str
    arguments: Dict[str, Any]  # Parsed JSON arguments

    @classmethod
    def from_openai(cls, data: Dict[str, Any]) -> "ToolCall":
        """Create from OpenAI tool call format."""
        import json
        return cls(
            id=data["id"],
            name=data["function"]["name"],
            arguments=json.loads(data["function"]["arguments"])
        )


@dataclass
class ToolResult:
    """
    Result of tool execution.
    """
    tool_call_id: str
    name: str
    content: str
    error: Optional[str] = None

    def to_openai_message(self) -> Dict[str, Any]:
        """Convert to OpenAI tool message format."""
        return {
            "role": "tool",
            "tool_call_id": self.tool_call_id,
            "content": self.content,
            "name": self.name,
        }


@dataclass
class ChatCompletionResult:
    """
    Result of a chat completion.
    """
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


@dataclass
class ProviderConfig:
    """
    Configuration for a model provider.
    """
    provider_id: str
    name: str
    provider_type: str  # llama_cpp, openai, custom
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    @classmethod
    def from_db_model(cls, db_model: Any, decrypted_api_key: Optional[str] = None) -> "ProviderConfig":
        """Create from database model."""
        return cls(
            provider_id=db_model.id,
            name=db_model.name,
            provider_type=db_model.provider_type,
            endpoint=db_model.endpoint,
            api_key=decrypted_api_key,
            config=db_model.config or {},
            is_active=db_model.is_active,
        )


# ============================================================================
# ModelProvider Protocol
# ============================================================================

@runtime_checkable
class ModelProvider(Protocol):
    """
    Protocol defining the interface for model providers.

    All providers (LlamaCppProvider, OpenAIProvider, CustomProvider)
    must implement this protocol to ensure consistent behavior.

    Usage:
        provider: ModelProvider = get_provider(config)
        async for chunk in provider.chat_stream(messages, model):
            yield chunk
    """

    @property
    def provider_id(self) -> str:
        """Unique identifier for this provider instance."""
        ...

    @property
    def provider_type(self) -> str:
        """Type of provider (llama_cpp, openai, custom)."""
        ...

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
        Send a chat completion request (non-streaming).

        Args:
            messages: List of chat messages.
            model: Model identifier to use.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            tools: List of available tools (function definitions).
            tool_choice: Tool selection mode ('auto', 'none', or specific tool).
            **kwargs: Additional provider-specific parameters.

        Returns:
            ChatCompletionResult with content or tool_calls.
        """
        ...

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

        Args:
            messages: List of chat messages.
            model: Model identifier to use.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            tools: List of available tools (function definitions).
            tool_choice: Tool selection mode.
            **kwargs: Additional provider-specific parameters.

        Yields:
            Text chunks from the model response.

        Raises:
            ProviderError: If the request fails.
        """
        ...

    async def list_models(self) -> List[ModelInfo]:
        """
        Get list of available models for this provider.

        Returns:
            List of ModelInfo objects describing available models.
        """
        ...

    async def validate_connection(self) -> bool:
        """
        Validate that the provider is reachable and properly configured.

        Returns:
            True if connection is valid, False otherwise.
        """
        ...


class ProviderError(Exception):
    """Exception raised when a provider operation fails."""
    def __init__(self, message: str, provider_id: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.provider_id = provider_id
        self.original_error = original_error


class ProviderNotFoundError(ProviderError):
    """Exception raised when a provider is not found."""
    pass


class ModelNotFoundError(ProviderError):
    """Exception raised when a model is not found."""
    pass
