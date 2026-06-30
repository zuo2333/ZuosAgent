"""
Memory management API endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.services.long_term_memory_service import LongTermMemoryService
from app.services.short_term_memory_service import ShortTermMemoryService
from app.services.memory_context_service import MemoryContextService
from app.schemas.memory import (
    MemorySearchRequest,
    MemorySearchResponse,
    MemorySearchResult,
    MemoryStatsResponse,
    LongTermMemoryResponse,
    ShortTermMemoryResponse,
    MemoryType
)

router = APIRouter(prefix="/memory", tags=["memory"])


# Default user ID for single-user scenarios
DEFAULT_USER_ID = "default"


@router.post("/extract")
async def extract_memories(
    session_id: str = Query(..., description="Session ID to extract memories from"),
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger memory extraction for a session.
    Extracts long-term memories from the session.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    from app.models import Session, Message
    from sqlalchemy.orm import selectinload

    # Get session with messages
    result = await db.execute(
        select(Session).options(selectinload(Session.messages)).where(Session.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Extract memories
    service = LongTermMemoryService(db)
    memories = await service.extract_from_session(
        user_id=user_id,
        session_id=session_id,
        messages=session.messages
    )

    return {
        "status": "success",
        "extracted_count": len(memories),
        "memory_ids": [str(m.id) for m in memories]
    }


@router.get("/search", response_model=MemorySearchResponse)
async def search_memories(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(10, ge=1, le=100, description="Maximum results"),
    memory_types: Optional[str] = Query(None, description="Comma-separated memory types"),
    min_importance: Optional[float] = Query(None, ge=0.0, le=1.0),
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search long-term memories by semantic similarity.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    # Parse memory types
    types = None
    if memory_types:
        types = [MemoryType(t.strip()) for t in memory_types.split(",") if t.strip()]

    service = LongTermMemoryService(db)
    results = await service.search(
        user_id=user_id,
        query=query,
        top_k=top_k,
        memory_types=types,
        min_importance=min_importance
    )

    search_results = [
        MemorySearchResult(
            memory=LongTermMemoryResponse(**service.to_response(memory)),
            similarity=similarity
        )
        for memory, similarity in results
    ]

    return MemorySearchResponse(
        results=search_results,
        query=query,
        total=len(search_results)
    )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a specific long-term memory.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = LongTermMemoryService(db)

    # Verify ownership
    memory = await service.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")

    if memory.user_id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    success = await service.delete(memory_id)
    return {"status": "success" if success else "failed"}


@router.get("/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get memory statistics for a user.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = LongTermMemoryService(db)
    stats = await service.get_stats(user_id)

    return MemoryStatsResponse(
        total_memories=stats["total_memories"],
        by_type=stats["by_type"],
        avg_importance=stats["avg_importance"],
        total_access_count=stats["total_access_count"],
        oldest_memory=stats["oldest_memory"],
        newest_memory=stats["newest_memory"]
    )


@router.get("/short-term/{session_id}", response_model=ShortTermMemoryResponse)
async def get_short_term_memory(
    session_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get short-term memory for a session.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = ShortTermMemoryService(db)
    memory = await service.get(session_id)

    if not memory:
        raise HTTPException(status_code=404, detail="Short-term memory not found")

    return ShortTermMemoryResponse(**service.to_response(memory))


@router.get("/context")
async def get_memory_context(
    session_id: str = Query(..., description="Session ID"),
    query: str = Query(..., description="Query for intent classification"),
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get memory context for LLM injection based on query intent.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = MemoryContextService(db)
    context, metadata = await service.build_context(
        user_id=user_id,
        session_id=session_id,
        query=query
    )

    return {
        "context": context,
        "metadata": metadata
    }
