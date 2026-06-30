"""
Session management API routes.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import SessionService
from app.schemas.api import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
    SessionListResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Dependency for session service."""
    return SessionService(db)


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    """
    Create a new chat session.

    Creates a session with optional configuration overrides.
    If not specified, defaults from global config will be used.
    """
    session = await service.create(data)
    return service.to_response(session)


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    skip: int = Query(default=0, ge=0, description="Number of sessions to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum sessions to return"),
    provider_id: Optional[str] = Query(default=None, description="Filter by provider ID"),
    service: SessionService = Depends(get_session_service)
):
    """
    Get list of chat sessions.

    Returns paginated list of sessions ordered by last updated.
    """
    sessions, total = await service.get_list(skip=skip, limit=limit, provider_id=provider_id)
    return SessionListResponse(
        sessions=[service.to_response(s) for s in sessions],
        total=total
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Get a specific session by ID.

    Returns the session details including configuration.
    """
    session = await service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return service.to_response(session)


@router.put("/{session_id}", response_model=SessionResponse)
@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    data: SessionUpdate,
    service: SessionService = Depends(get_session_service)
):
    """
    Update a session.

    Only provided fields will be updated.
    """
    session = await service.update(session_id, data)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return service.to_response(session)


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service)
):
    """
    Delete a session.

    Also deletes all associated messages and tool calls.
    """
    deleted = await service.delete(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return None
