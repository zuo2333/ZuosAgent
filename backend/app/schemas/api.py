"""
API schemas for request/response models.
"""
from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from decimal import Decimal


# ============================================================================
# Session Schemas
# ============================================================================

class SessionCreate(BaseModel):
    """Schema for creating a new session."""
    title: Optional[str] = Field(default=None, max_length=100)
    provider_id: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    enabled_tools: Optional[List[str]] = Field(default=["web_search", "db_query"])

    class Config:
        json_schema_extra = {
            "example": {
                "title": "New Chat",
                "provider_id": "local-llama",
                "model": "qwen3.6:27b",
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 4096,
                "enabled_tools": ["web_search", "db_query"]
            }
        }


class SessionUpdate(BaseModel):
    """Schema for updating a session."""
    title: Optional[str] = Field(default=None, max_length=100)
    provider_id: Optional[str] = Field(default=None, max_length=100)
    model: Optional[str] = Field(default=None, max_length=100)
    system_prompt: Optional[str] = None
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    enabled_tools: Optional[List[str]] = None


class SessionResponse(BaseModel):
    """Schema for session response."""
    id: str
    title: Optional[str] = None
    provider_id: Optional[str] = None
    model: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    enabled_tools: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime_utc(self, dt: datetime, _info):
        """Serialize datetime with UTC timezone indicator."""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


class SessionListResponse(BaseModel):
    """Schema for session list response."""
    sessions: List[SessionResponse]
    total: int


# ============================================================================
# Message Schemas
# ============================================================================

class MessageCreate(BaseModel):
    """Schema for creating a message."""
    role: Literal["user", "assistant", "system", "tool"]
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = Field(default=None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Hello, how are you?"
            }
        }


class MessageResponse(BaseModel):
    """Schema for message response."""
    id: str
    session_id: str
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

    @field_serializer('created_at')
    def serialize_datetime_utc(self, dt: datetime, _info):
        """Serialize datetime with UTC timezone indicator."""
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%f") + "Z"


class MessageListResponse(BaseModel):
    """Schema for message list response."""
    messages: List[MessageResponse]
    total: int


# ============================================================================
# Provider Schemas
# ============================================================================

class ProviderCreate(BaseModel):
    """Schema for creating a provider."""
    id: Optional[str] = Field(default=None, max_length=100)
    name: str = Field(..., max_length=255)
    provider_type: Literal["llama_cpp", "openai", "custom"]
    base_url: Optional[str] = Field(default=None, max_length=500)
    api_key: Optional[str] = Field(default=None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "openai-main",
                "name": "OpenAI Main",
                "provider_type": "openai",
                "base_url": "https://api.openai.com/v1",
                "api_key": "sk-xxx",
                "is_active": True
            }
        }


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""
    name: Optional[str] = Field(default=None, max_length=255)
    provider_type: Optional[Literal["llama_cpp", "openai", "custom"]] = None
    base_url: Optional[str] = Field(default=None, max_length=500)
    api_key: Optional[str] = Field(default=None, max_length=500)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ProviderResponse(BaseModel):
    """Schema for provider response (without API key)."""
    id: str
    name: str
    provider_type: str
    base_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: bool

    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """Schema for provider list response."""
    providers: List[ProviderResponse]
    total: int


# ============================================================================
# Global Config Schemas
# ============================================================================

class GlobalConfigUpdate(BaseModel):
    """Schema for updating global configuration."""
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: Optional[float] = Field(default=None, ge=0, le=2)
    default_max_tokens: Optional[int] = Field(default=None, ge=1)
    default_system_prompt: Optional[str] = None
    db_query_allowed_tables: Optional[List[str]] = None
    web_search_timeout_seconds: Optional[int] = Field(default=None, ge=1, le=300)
    web_search_max_results: Optional[int] = Field(default=None, ge=1, le=20)
    db_query_timeout_seconds: Optional[int] = Field(default=None, ge=1, le=60)
    db_query_max_rows: Optional[int] = Field(default=None, ge=1, le=1000)


class GlobalConfigResponse(BaseModel):
    """Schema for global configuration response."""
    default_provider: Optional[str] = None
    default_model: Optional[str] = None
    default_temperature: Optional[float] = None
    default_max_tokens: Optional[int] = None
    default_system_prompt: Optional[str] = None
    db_query_allowed_tables: Optional[List[str]] = None
    web_search_timeout_seconds: Optional[int] = None
    web_search_max_results: Optional[int] = None
    db_query_timeout_seconds: Optional[int] = None
    db_query_max_rows: Optional[int] = None


# ============================================================================
# Chat Request/Response Schemas
# ============================================================================

class ChatRequest(BaseModel):
    """Schema for chat request."""
    session_id: str
    message: str
    stream: bool = True
    temperature: Optional[float] = Field(default=None, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=None, ge=1)

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "uuid-here",
                "message": "What is the capital of France?",
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    database: Optional[str] = None


# ============================================================================
# SSE Event Schemas
# ============================================================================

class SSEEvent(BaseModel):
    """Base schema for SSE events."""
    event: str
    data: Dict[str, Any]


class ContentDeltaEvent(BaseModel):
    """SSE event for streaming content."""
    delta: str


class ToolCallStartEvent(BaseModel):
    """SSE event for tool call start."""
    tool_name: str
    tool_call_id: str


class ToolCallEndEvent(BaseModel):
    """SSE event for tool call end."""
    tool_call_id: str
    status: str
    result: Optional[str] = None


class DoneEvent(BaseModel):
    """SSE event for completion."""
    pass


class ErrorEvent(BaseModel):
    """SSE event for errors."""
    message: str
    code: Optional[str] = None
