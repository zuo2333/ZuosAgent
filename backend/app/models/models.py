"""
SQLAlchemy database models
"""
import uuid
import json
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, DateTime, Numeric, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


class GlobalConfig(Base):
    """
    Global configuration key-value store.
    Stores system-wide settings like default provider, model, temperature, etc.
    """
    __tablename__ = "global_config"

    key = Column(String(100), primary_key=True, nullable=False)
    value = Column(JSONB, nullable=True)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<GlobalConfig(key={self.key})>"


class Session(Base):
    """
    Chat session model.
    Each session has its own configuration and contains multiple messages.
    """
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    title = Column(String(100), nullable=True)
    provider_id = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    system_prompt = Column(Text, nullable=True)
    temperature = Column(Numeric(3, 2), nullable=True)
    max_tokens = Column(Integer, nullable=True)
    enabled_tools = Column(
        JSONB,
        nullable=False,
        default=lambda: json.dumps(["web_search", "db_query"])
    )
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    tool_calls = relationship(
        "ToolCall",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title={self.title})>"


class Message(Base):
    """
    Chat message model.
    Supports roles: user, assistant, system, tool.
    Can contain tool_calls (for assistant messages) or tool_call_id (for tool messages).
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    role = Column(String(20), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=True)
    tool_calls = Column(JSONB, nullable=True)  # Tool call requests (assistant messages)
    tool_call_id = Column(String(100), nullable=True)  # Tool call ID (tool messages)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    session = relationship("Session", back_populates="messages")
    tool_calls_rel = relationship(
        "ToolCall",
        back_populates="message",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"


class Provider(Base):
    """
    Model provider configuration.
    Supports llama_cpp, openai, and custom provider types.
    API keys are encrypted before storage.
    """
    __tablename__ = "providers"

    id = Column(String(100), primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)
    provider_type = Column(String(50), nullable=False)  # llama_cpp, openai, custom
    endpoint = Column(String(500), nullable=True)
    api_key = Column(String(500), nullable=True)  # Encrypted storage
    config = Column(JSONB, nullable=True)  # Additional provider-specific config
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Provider(id={self.id}, name={self.name}, type={self.provider_type})>"


class ToolCall(Base):
    """
    Tool call execution record.
    Tracks tool invocations during agent execution.
    """
    __tablename__ = "tool_calls"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    message_id = Column(
        UUID(as_uuid=False),
        ForeignKey("messages.id", ondelete="SET NULL"),
        nullable=True
    )
    tool_name = Column(String(100), nullable=False)
    tool_input = Column(JSONB, nullable=True)
    tool_output = Column(JSONB, nullable=True)
    status = Column(String(20), nullable=False)  # success, failed, denied, timeout
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    session = relationship("Session", back_populates="tool_calls")
    message = relationship("Message", back_populates="tool_calls_rel")

    def __repr__(self) -> str:
        return f"<ToolCall(id={self.id}, tool_name={self.tool_name}, status={self.status})>"
