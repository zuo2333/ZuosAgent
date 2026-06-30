"""
User profile API endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.services.user_profile_service import UserProfileService
from app.schemas.memory import (
    UserProfileResponse,
    UserProfileUpdate,
    ProfileInferRequest,
    ResponseStyle,
    TechLevel
)

router = APIRouter(prefix="/profile", tags=["profile"])


# Default user ID for single-user scenarios
DEFAULT_USER_ID = "default"


class ProfileUpdateRequest(BaseModel):
    """Profile update request"""
    nickname: Optional[str] = None
    language: Optional[str] = None
    response_style: Optional[dict] = None
    tech_level: Optional[str] = None
    interests: Optional[List[str]] = None


@router.get("", response_model=UserProfileResponse)
async def get_profile(
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = UserProfileService(db)
    profile = await service.get_or_create(user_id)

    return UserProfileResponse(**service.to_response(profile))


@router.patch("", response_model=UserProfileResponse)
async def update_profile(
    data: ProfileUpdateRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile fields.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = UserProfileService(db)

    profile = await service.update(
        user_id=user_id,
        nickname=data.nickname,
        language=data.language,
        response_style=data.response_style,
        tech_level=data.tech_level,
        interests=data.interests
    )

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return UserProfileResponse(**service.to_response(profile))


@router.post("/infer")
async def infer_profile(
    data: ProfileInferRequest,
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger profile inference from recent sessions.
    Uses LLM to analyze session history and update profile.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    from app.models import Session
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    service = UserProfileService(db)

    # Get recent sessions
    if data.session_id:
        # Analyze specific session
        result = await db.execute(
            select(Session).where(Session.id == data.session_id)
        )
        sessions = [result.scalar_one_or_none()] if result else []
    else:
        # Get recent sessions (last 10)
        result = await db.execute(
            select(Session)
            .order_by(Session.updated_at.desc())
            .limit(10)
        )
        sessions = list(result.scalars().all())

    if not sessions:
        raise HTTPException(status_code=404, detail="No sessions found for inference")

    profile = await service.infer_profile(
        user_id=user_id,
        sessions=sessions,
        force=data.force
    )

    return {
        "status": "success",
        "profile_version": profile.profile_version if profile else 0,
        "last_inferred_at": profile.last_inferred_at.isoformat() if profile and profile.last_inferred_at else None
    }


@router.get("/knowledge-graph")
async def get_knowledge_graph(
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the user's knowledge graph.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = UserProfileService(db)
    profile = await service.get_or_create(user_id)

    return profile.knowledge_graph or {"entities": [], "relations": []}


@router.post("/knowledge-graph/entities")
async def add_knowledge_entity(
    entity_id: str = Query(..., description="Entity ID"),
    name: str = Query(..., description="Entity name"),
    entity_type: str = Query(..., description="Entity type (person, company, project, etc.)"),
    attributes: Optional[dict] = None,
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Add an entity to the knowledge graph.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = UserProfileService(db)
    profile = await service.add_entity(
        user_id=user_id,
        entity_id=entity_id,
        name=name,
        entity_type=entity_type,
        attributes=attributes
    )

    return {
        "status": "success",
        "profile_version": profile.profile_version
    }


@router.post("/knowledge-graph/relations")
async def add_knowledge_relation(
    source_id: str = Query(..., description="Source entity ID"),
    relation: str = Query(..., description="Relation type"),
    target_id: str = Query(..., description="Target entity ID"),
    user_id: str = Query(DEFAULT_USER_ID, description="User ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a relation to the knowledge graph.
    """
    if not settings.MEMORY_ENABLED:
        raise HTTPException(status_code=503, detail="Memory system is disabled")

    service = UserProfileService(db)
    profile = await service.add_relation(
        user_id=user_id,
        source_id=source_id,
        relation=relation,
        target_id=target_id
    )

    return {
        "status": "success",
        "profile_version": profile.profile_version
    }
