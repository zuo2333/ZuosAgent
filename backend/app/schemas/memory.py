"""
Pydantic schemas for memory system API
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


# Re-export MemoryType from models
class MemoryType(str, Enum):
    """Long-term memory types"""
    FACT = "fact"
    PREFERENCE = "preference"
    EVENT = "event"


class ResponseVerbosity(str, Enum):
    """Response verbosity levels"""
    CONCISE = "concise"
    NORMAL = "normal"
    DETAILED = "detailed"


class TechLevel(str, Enum):
    """User technical level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


# ============== Short-term Memory Schemas ==============

class EntityItem(BaseModel):
    """Single entity item"""
    name: str
    type: str = Field(..., description="Entity type: person, project, technology, etc.")
    mentions: int = Field(default=1, description="Number of times mentioned")


class PendingTask(BaseModel):
    """Pending task item"""
    task: str
    status: str = Field(default="pending", description="Task status: pending, in_progress, completed")
    created_at: Optional[datetime] = None


class ShortTermMemoryResponse(BaseModel):
    """Short-term memory response"""
    session_id: str
    summary: Optional[str] = None
    entities: Dict[str, List[str]] = Field(default_factory=dict)
    pending_tasks: List[PendingTask] = Field(default_factory=list)
    total_tokens: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ShortTermMemoryUpdate(BaseModel):
    """Short-term memory update request"""
    summary: Optional[str] = None
    entities: Optional[Dict[str, List[str]]] = None
    pending_tasks: Optional[List[PendingTask]] = None


# ============== Long-term Memory Schemas ==============

class LongTermMemoryCreate(BaseModel):
    """Request to create a long-term memory"""
    content: str
    memory_type: MemoryType
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    source_session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LongTermMemoryResponse(BaseModel):
    """Long-term memory response"""
    id: str
    user_id: str
    content: str
    memory_type: str
    importance: float
    decay_factor: float
    access_count: int
    last_accessed_at: Optional[datetime] = None
    source_session_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MemorySearchRequest(BaseModel):
    """Memory search request"""
    query: str
    top_k: int = Field(default=10, ge=1, le=100)
    memory_types: Optional[List[MemoryType]] = None
    min_importance: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class MemorySearchResult(BaseModel):
    """Single search result"""
    memory: LongTermMemoryResponse
    similarity: float = Field(..., description="Cosine similarity score")


class MemorySearchResponse(BaseModel):
    """Memory search response"""
    results: List[MemorySearchResult]
    query: str
    total: int


class MemoryStatsResponse(BaseModel):
    """Memory statistics response"""
    total_memories: int
    by_type: Dict[str, int]
    avg_importance: float
    total_access_count: int
    oldest_memory: Optional[datetime] = None
    newest_memory: Optional[datetime] = None


# ============== User Profile Schemas ==============

class ResponseStyle(BaseModel):
    """User response style preferences"""
    verbosity: ResponseVerbosity = ResponseVerbosity.NORMAL
    include_code_examples: bool = True
    language: str = "zh-CN"


class KnowledgeEntity(BaseModel):
    """Knowledge graph entity"""
    id: str
    name: str
    type: str = Field(..., description="Entity type: person, company, project, etc.")
    attributes: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeRelation(BaseModel):
    """Knowledge graph relation"""
    source: str = Field(..., description="Source entity ID")
    relation: str = Field(..., description="Relation type")
    target: str = Field(..., description="Target entity ID")


class KnowledgeGraph(BaseModel):
    """User knowledge graph"""
    entities: List[KnowledgeEntity] = Field(default_factory=list)
    relations: List[KnowledgeRelation] = Field(default_factory=list)


class UserProfileResponse(BaseModel):
    """User profile response"""
    user_id: str
    nickname: Optional[str] = None
    language: str = "zh-CN"
    response_style: ResponseStyle
    tech_level: TechLevel = TechLevel.INTERMEDIATE
    interests: List[str] = Field(default_factory=list)
    task_distribution: Dict[str, int] = Field(default_factory=dict)
    active_hours: Dict[str, int] = Field(default_factory=dict)
    tool_usage: Dict[str, int] = Field(default_factory=dict)
    knowledge_graph: KnowledgeGraph
    profile_version: int = 1
    last_inferred_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    """User profile update request"""
    nickname: Optional[str] = None
    language: Optional[str] = None
    response_style: Optional[ResponseStyle] = None
    tech_level: Optional[TechLevel] = None
    interests: Optional[List[str]] = None


class ProfileInferRequest(BaseModel):
    """Request to trigger profile inference"""
    session_id: Optional[str] = Field(default=None, description="Specific session to analyze")
    force: bool = Field(default=False, description="Force inference even if recently done")


# ============== Memory Context Schemas ==============

class MemoryIntent(str, Enum):
    """Memory injection intent"""
    NONE = "none"                    # No memory needed
    SHORT_TERM = "short_term"        # Need short-term memory only
    LONG_TERM = "long_term"          # Need long-term memory only
    BOTH = "both"                    # Need both memory types


class MemoryContext(BaseModel):
    """Formatted memory context for LLM injection"""
    user_profile: Optional[str] = None
    long_term_memories: Optional[str] = None
    short_term_memory: Optional[str] = None
    total_tokens: int = 0
