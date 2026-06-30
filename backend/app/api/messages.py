"""
Message management API routes.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import SessionService, MessageService
from app.schemas.api import (
    MessageCreate,
    MessageResponse,
    MessageListResponse,
)

router = APIRouter(tags=["messages"])

# Dependency for services
def get_message_service(db: AsyncSession = Depends(get_db)) -> MessageService:
    """Dependency for message service."""
    return MessageService(db)


def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Dependency for session service."""
    return SessionService(db)


@router.get(
    "/sessions/{session_id}/messages",
    response_model=MessageListResponse,
    summary="Get session messages"
)
async def list_messages(
    session_id: str,
    skip: int = Query(default=0, ge=0, description="Number of messages to skip"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum messages to return"),
    role: Optional[str] = Query(default=None, description="Filter by role (user, assistant, system, tool)"),
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Get messages for a session.

    Returns paginated list of messages ordered by creation time.
    """
    # Verify session exists
    session = await session_service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages, total = await message_service.get_by_session(
        session_id=session_id,
        skip=skip,
        limit=limit,
        role=role
    )
    return MessageListResponse(
        messages=[message_service.to_response(m) for m in messages],
        total=total
    )


@router.post(
    "/sessions/{session_id}/messages",
    response_model=MessageResponse,
    status_code=201,
    summary="Add message to session"
)
async def create_message(
    session_id: str,
    data: MessageCreate,
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Add a message to a session.

    Used for manually adding messages (e.g., system messages, tool responses).
    For chat, use the /chat endpoint instead.
    """
    # Verify session exists
    session = await session_service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    message = await message_service.create(session_id, data)
    return message_service.to_response(message)


@router.delete(
    "/sessions/{session_id}/messages/{message_id}",
    status_code=204,
    summary="Delete a message"
)
async def delete_message(
    session_id: str,
    message_id: str,
    message_service: MessageService = Depends(get_message_service),
    session_service: SessionService = Depends(get_session_service)
):
    """
    Delete a specific message.

    Note: This may break conversation context if the message
    is in the middle of a thread.
    """
    # Verify session exists
    session = await session_service.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    message = await message_service.get(message_id)
    if not message or str(message.session_id) != session_id:
        raise HTTPException(status_code=404, detail="Message not found")

    await message_service.delete(message_id)
    return None
