"""
Memory-related SQLAlchemy models
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Numeric, ForeignKey, JSON, Index, Float
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.core.database import Base
import enum

# Import pgvector for SQLAlchemy
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    Vector = None


class MemoryType(str, enum.Enum):
    """Long-term memory types"""
    FACT = "fact"           # 事实性记忆：用户陈述的事实
    PREFERENCE = "preference"  # 偏好性记忆：用户的偏好设置
    EVENT = "event"         # 事件性记忆：重要交互事件


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


class ShortTermMemory(Base):
    """
    Short-term memory for a session.
    1:1 relationship with Session.
    Stores session summary, extracted entities, and pending tasks.
    """
    __tablename__ = "short_term_memories"

    session_id = Column(
        UUID(as_uuid=False),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    summary = Column(Text, nullable=True)
    entities = Column(JSONB, nullable=False, default=dict)  # {"persons": [], "projects": [], "technologies": []}
    pending_tasks = Column(JSONB, nullable=False, default=list)  # [{"task": str, "status": str}]
    total_tokens = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("Session", backref="short_term_memory", uselist=False)

    def __repr__(self) -> str:
        return f"<ShortTermMemory(session_id={self.session_id}, tokens={self.total_tokens})>"


class LongTermMemory(Base):
    """
    Long-term memory with vector embedding.
    Supports semantic retrieval via pgvector.
    """
    __tablename__ = "long_term_memories"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    memory_type = Column(String(20), nullable=False, index=True)  # fact, preference, event
    # Use pgvector's Vector type (1536 dimensions for OpenAI embeddings)
    # Fallback to ARRAY if pgvector not installed
    embedding = Column(Vector(1536) if HAS_PGVECTOR else ARRAY(Float, dimensions=1), nullable=True)
    importance = Column(Numeric(3, 2), nullable=False, default=Decimal("0.5"))
    decay_factor = Column(Numeric(3, 2), nullable=False, default=Decimal("1.0"))
    access_count = Column(Integer, nullable=False, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    source_session_id = Column(UUID(as_uuid=False), nullable=True)
    extra_data = Column(JSONB, nullable=False, default=dict)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<LongTermMemory(id={self.id}, type={self.memory_type})>"

    @property
    def effective_importance(self) -> float:
        """Calculate effective importance considering decay"""
        return float(self.importance) * float(self.decay_factor)


class UserProfile(Base):
    """
    User profile with preferences, behavior patterns, and knowledge graph.
    """
    __tablename__ = "user_profiles"

    user_id = Column(String(100), primary_key=True, nullable=False)
    nickname = Column(String(100), nullable=True)
    language = Column(String(10), nullable=False, default="zh-CN")
    response_style = Column(JSONB, nullable=False, default=lambda: {"verbosity": "normal"})
    tech_level = Column(String(20), nullable=False, default="intermediate")  # beginner, intermediate, expert
    interests = Column(JSONB, nullable=False, default=list)  # ["AI", "Python", "Web Development"]
    task_distribution = Column(JSONB, nullable=False, default=dict)  # {"programming": 10, "writing": 5}
    active_hours = Column(JSONB, nullable=False, default=dict)  # {"0": 0, "1": 0, ..., "23": 5}
    tool_usage = Column(JSONB, nullable=False, default=dict)  # {"web_search": 20, "db_query": 5}
    knowledge_graph = Column(JSONB, nullable=False, default=lambda: {"entities": [], "relations": []})
    profile_version = Column(Integer, nullable=False, default=1)
    last_inferred_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, nickname={self.nickname})>"
