"""
Chat-related Pydantic schemas for API request/response models.
These schemas define the data structures for chat completions.
"""
from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


# ============================================================================
# Chat Message Schemas
# ============================================================================

class ChatMessage(BaseModel):
    """
    Chat message schema following OpenAI format.
    Supports user, assistant, system, and tool roles.
    """
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None  # For tool messages
    tool_calls: Optional[List["ToolCall"]] = None  # For assistant messages with tool calls
    tool_call_id: Optional[str] = None  # For tool response messages

    class Config:
        json_schema_extra = {
            "examples": [
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you!"},
                {"role": "system", "content": "You are a helpful assistant."},
            ]
        }


class ToolCall(BaseModel):
    """
    Tool call request from the model.
    Follows OpenAI's function calling format.
    """
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:24]}")
    type: Literal["function"] = "function"
    function: "FunctionCall"

    class Config:
        json_schema_extra = {
            "example": {
                "id": "call_abc123",
                "type": "function",
                "function": {
                    "name": "web_search",
                    "arguments": "{\"query\": \"latest AI news\"}"
                }
            }
        }


class FunctionCall(BaseModel):
    """Function call with name and JSON arguments."""
    name: str
    arguments: str  # JSON string of parameters


class ToolResult(BaseModel):
    """
    Tool execution result.
    Used to format tool responses for the model.
    """
    tool_call_id: str
    role: Literal["tool"] = "tool"
    content: str
    name: Optional[str] = None  # Tool name for reference

    class Config:
        json_schema_extra = {
            "example": {
                "tool_call_id": "call_abc123",
                "role": "tool",
                "content": "Search results: ...",
                "name": "web_search"
            }
        }


# Update forward references
ChatMessage.model_rebuild()
ToolCall.model_rebuild()


# ============================================================================
# Model Info Schema
# ============================================================================

class ModelInfo(BaseModel):
    """
    Information about an available model.
    """
    id: str
    name: str
    provider: str
    owned_by: Optional[str] = None
    context_length: Optional[int] = None
    supports_tools: bool = True
    supports_vision: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "gpt-4",
                "name": "GPT-4",
                "provider": "openai",
                "owned_by": "openai",
                "context_length": 8192,
                "supports_tools": True,
                "supports_vision": False
            }
        }


# ============================================================================
# Chat Completion Request/Response Schemas
# ============================================================================

class ChatCompletionRequest(BaseModel):
    """
    Chat completion request schema.
    Compatible with OpenAI's chat completion API.
    """
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    stream: bool = False
    tools: Optional[List["ToolDefinition"]] = None
    tool_choice: Optional[Union[Literal["auto", "none"], Dict[str, Any]]] = None
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    frequency_penalty: Optional[float] = Field(default=0, ge=-2, le=2)
    user: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "What is the capital of France?"}
                ],
                "temperature": 0.7,
                "stream": False
            }
        }


class ToolDefinition(BaseModel):
    """Tool definition for function calling."""
    type: Literal["function"] = "function"
    function: "FunctionDefinition"


class FunctionDefinition(BaseModel):
    """Function definition with name, description, and parameters schema."""
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema for parameters


# Update forward references
ChatCompletionRequest.model_rebuild()
ToolDefinition.model_rebuild()


class ChatCompletionChoice(BaseModel):
    """Single choice in chat completion response."""
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class Usage(BaseModel):
    """Token usage statistics."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """
    Chat completion response schema.
    Compatible with OpenAI's chat completion API.
    """
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: Optional[Usage] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "chatcmpl-abc123",
                "object": "chat.completion",
                "created": 1677858242,
                "model": "gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "The capital of France is Paris."
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 20,
                    "completion_tokens": 10,
                    "total_tokens": 30
                }
            }
        }


# ============================================================================
# Streaming Response Schemas
# ============================================================================

class ChatCompletionChunk(BaseModel):
    """
    Streaming chunk for chat completion.
    Used for SSE (Server-Sent Events) streaming responses.
    """
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int
    model: str
    choices: List["ChunkChoice"]


class ChunkChoice(BaseModel):
    """Single choice in a streaming chunk."""
    index: int
    delta: "ChatMessageDelta"
    finish_reason: Optional[str] = None


class ChatMessageDelta(BaseModel):
    """Delta message in streaming response."""
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


# Update forward references
ChatCompletionChunk.model_rebuild()
ChunkChoice.model_rebuild()
ChatMessageDelta.model_rebuild()
