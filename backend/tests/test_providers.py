"""
Unit tests for ModelProvider protocol and implementations.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, AsyncIterator

from app.providers.base import (
    ModelProvider,
    ProviderConfig,
    ChatMessage,
    ChatCompletionResult,
    ToolCall,
    ToolResult,
    ModelInfo,
    ProviderError,
)
from app.providers.factory import create_provider
from app.providers.openai import OpenAIProvider
from app.providers.openai_compatible import OpenAICompatibleProvider
from app.providers.llama_cpp import LlamaCppProvider


class TestModelProviderProtocol:
    """Tests for ModelProvider protocol compliance."""

    def test_provider_has_required_attributes(self):
        """Test that providers have required attributes."""
        config = ProviderConfig(
            provider_id="test-provider",
            name="Test Provider",
            provider_type="openai",
            api_key="test-key",
        )
        provider = OpenAIProvider(config)
        assert hasattr(provider, "provider_id")
        assert hasattr(provider, "provider_type")
        assert provider.provider_id == "test-provider"
        assert provider.provider_type == "openai"

    def test_provider_has_required_methods(self):
        """Test that providers have required methods."""
        config = ProviderConfig(
            provider_id="test-provider",
            name="Test Provider",
            provider_type="openai",
            api_key="test-key",
        )
        provider = OpenAIProvider(config)
        assert hasattr(provider, "chat")
        assert hasattr(provider, "chat_stream")
        assert hasattr(provider, "list_models")
        assert hasattr(provider, "validate_connection")
        assert callable(provider.chat)
        assert callable(provider.chat_stream)
        assert callable(provider.list_models)
        assert callable(provider.validate_connection)


class TestOpenAIProvider:
    """Tests for OpenAI provider implementation."""

    @pytest.fixture
    def provider_config(self):
        """Create a test provider configuration."""
        return ProviderConfig(
            provider_id="openai-test",
            name="OpenAI Test",
            provider_type="openai",
            api_key="sk-test-key",
        )

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch("app.providers.openai.AsyncOpenAI") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    @pytest.mark.asyncio
    async def test_chat_non_streaming(self, provider_config, mock_openai_client):
        """Test non-streaming chat completion."""
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello, how can I help?"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.choices[0].message.tool_calls = None
        mock_response.usage = MagicMock()
        mock_response.usage.total_tokens = 100

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(provider_config)
        messages = [ChatMessage(role="user", content="Hello")]

        result = await provider.chat(
            messages=messages,
            model="gpt-4",
            temperature=0.7,
        )

        assert result.content == "Hello, how can I help?"
        assert result.finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_chat_with_tool_calls(self, provider_config, mock_openai_client):
        """Test chat completion with tool calls."""
        # Mock tool call response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = None
        mock_response.choices[0].finish_reason = "tool_calls"
        mock_response.choices[0].message.tool_calls = [MagicMock()]
        mock_response.choices[0].message.tool_calls[0].id = "call_123"
        mock_response.choices[0].message.tool_calls[0].function.name = "web_search"
        mock_response.choices[0].message.tool_calls[0].function.arguments = '{"query": "test"}'

        mock_openai_client.chat.completions.create = AsyncMock(return_value=mock_response)

        provider = OpenAIProvider(provider_config)
        messages = [ChatMessage(role="user", content="Search for test")]

        tools = [{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}
            }
        }]

        result = await provider.chat(
            messages=messages,
            model="gpt-4",
            tools=tools,
        )

        assert result.tool_calls is not None
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].name == "web_search"
        assert result.tool_calls[0].arguments == {"query": "test"}

    @pytest.mark.asyncio
    async def test_list_models(self, provider_config, mock_openai_client):
        """Test listing available models."""
        mock_models = MagicMock()
        mock_models.data = [
            MagicMock(id="gpt-4", owned_by="openai"),
            MagicMock(id="gpt-3.5-turbo", owned_by="openai"),
        ]
        mock_openai_client.models.list = AsyncMock(return_value=mock_models)

        provider = OpenAIProvider(provider_config)
        models = await provider.list_models()

        assert len(models) == 2
        assert models[0].id == "gpt-4"
        assert models[1].id == "gpt-3.5-turbo"

    @pytest.mark.asyncio
    async def test_validate_connection_success(self, provider_config, mock_openai_client):
        """Test successful connection validation."""
        mock_models = MagicMock()
        mock_models.data = [MagicMock()]
        mock_openai_client.models.list = AsyncMock(return_value=mock_models)

        provider = OpenAIProvider(provider_config)
        is_valid = await provider.validate_connection()

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_connection_failure(self, provider_config, mock_openai_client):
        """Test failed connection validation."""
        mock_openai_client.models.list = AsyncMock(side_effect=Exception("Connection failed"))

        provider = OpenAIProvider(provider_config)
        is_valid = await provider.validate_connection()

        assert is_valid is False


class TestLlamaCppProvider:
    """Tests for LlamaCpp provider implementation."""

    @pytest.fixture
    def provider_config(self):
        """Create a test provider configuration."""
        return ProviderConfig(
            provider_id="llamacpp-test",
            name="LlamaCpp Test",
            provider_type="llama_cpp",
            endpoint="http://localhost:8080",
        )

    def test_provider_type(self, provider_config):
        """Test provider type is correct."""
        provider = LlamaCppProvider(provider_config)
        assert provider.provider_type == "llama_cpp"

    @pytest.mark.asyncio
    async def test_uses_openai_compatible_api(self, provider_config):
        """Test that LlamaCpp uses OpenAI-compatible API."""
        provider = LlamaCppProvider(provider_config)
        # LlamaCpp provider should work with OpenAI-compatible endpoints
        assert hasattr(provider, "chat")
        assert hasattr(provider, "chat_stream")


class TestProviderFactory:
    """Tests for provider factory function."""

    def test_create_openai_provider(self):
        """Test creating OpenAI provider."""
        config = ProviderConfig(
            provider_id="openai",
            name="OpenAI",
            provider_type="openai",
            api_key="sk-test",
        )
        provider = create_provider(config)
        assert isinstance(provider, OpenAIProvider)

    def test_create_llamacpp_provider(self):
        """Test creating LlamaCpp provider."""
        config = ProviderConfig(
            provider_id="llamacpp",
            name="LlamaCpp",
            provider_type="llama_cpp",
            endpoint="http://localhost:8080",
        )
        provider = create_provider(config)
        assert isinstance(provider, LlamaCppProvider)

    def test_create_custom_provider(self):
        """Test creating custom provider."""
        config = ProviderConfig(
            provider_id="custom",
            name="Custom",
            provider_type="custom",
            endpoint="http://localhost:8080/v1",
            api_key="test-key",
        )
        provider = create_provider(config)
        assert isinstance(provider, OpenAICompatibleProvider)

    def test_create_unknown_provider_raises_error(self):
        """Test that unknown provider type raises error."""
        config = ProviderConfig(
            provider_id="unknown",
            name="Unknown",
            provider_type="unknown_type",
        )
        with pytest.raises(ValueError, match="Unknown provider type"):
            create_provider(config)


class TestChatMessage:
    """Tests for ChatMessage data structure."""

    def test_create_user_message(self):
        """Test creating a user message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.tool_calls is None

    def test_create_assistant_message_with_tool_calls(self):
        """Test creating an assistant message with tool calls."""
        from app.providers.base import ToolCallData, FunctionCallData

        tool_calls = [
            ToolCallData(
                id="call_123",
                function=FunctionCallData(name="web_search", arguments='{"query": "test"}')
            )
        ]
        msg = ChatMessage(role="assistant", content=None, tool_calls=tool_calls)
        assert msg.role == "assistant"
        assert msg.tool_calls is not None
        assert len(msg.tool_calls) == 1

    def test_create_tool_result_message(self):
        """Test creating a tool result message."""
        msg = ChatMessage(
            role="tool",
            tool_call_id="call_123",
            content="Search results..."
        )
        assert msg.role == "tool"
        assert msg.tool_call_id == "call_123"


class TestToolCall:
    """Tests for ToolCall data structure."""

    def test_from_openai_format(self):
        """Test creating ToolCall from OpenAI format."""
        data = {
            "id": "call_abc123",
            "function": {
                "name": "web_search",
                "arguments": '{"query": "python async"}'
            }
        }
        tool_call = ToolCall.from_openai(data)
        assert tool_call.id == "call_abc123"
        assert tool_call.name == "web_search"
        assert tool_call.arguments == {"query": "python async"}

    def test_to_openai_message(self):
        """Test converting ToolResult to OpenAI message format."""
        result = ToolResult(
            tool_call_id="call_123",
            name="web_search",
            content="Search results..."
        )
        msg = result.to_openai_message()
        assert msg["role"] == "tool"
        assert msg["tool_call_id"] == "call_123"
        assert msg["content"] == "Search results..."


class TestModelInfo:
    """Tests for ModelInfo data structure."""

    def test_create_model_info(self):
        """Test creating ModelInfo."""
        info = ModelInfo(
            id="gpt-4",
            name="GPT-4",
            provider="openai",
            context_length=8192,
            supports_tools=True,
        )
        assert info.id == "gpt-4"
        assert info.supports_tools is True

    def test_to_dict(self):
        """Test converting ModelInfo to dictionary."""
        info = ModelInfo(
            id="gpt-4",
            name="GPT-4",
            provider="openai",
            owned_by="openai",
        )
        d = info.to_dict()
        assert d["id"] == "gpt-4"
        assert d["name"] == "GPT-4"
        assert d["provider"] == "openai"


class TestProviderError:
    """Tests for provider error handling."""

    def test_provider_error(self):
        """Test creating ProviderError."""
        error = ProviderError(
            message="Connection failed",
            provider_id="test-provider",
        )
        assert str(error) == "Connection failed"
        assert error.provider_id == "test-provider"

    def test_provider_error_with_original(self):
        """Test ProviderError with original exception."""
        original = ValueError("Original error")
        error = ProviderError(
            message="Wrapped error",
            provider_id="test-provider",
            original_error=original,
        )
        assert error.original_error == original
