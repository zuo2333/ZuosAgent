"""
Session service for managing chat sessions.
"""
import json
from typing import Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models import Session, Message
from app.schemas.api import SessionCreate, SessionUpdate


class SessionService:
    """Service for managing chat sessions."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the session service.

        Args:
            db: AsyncSession for database operations.
        """
        self.db = db

    async def create(self, data: SessionCreate) -> Session:
        """
        Create a new session.

        Args:
            data: Session creation data.

        Returns:
            Created Session object.
        """
        session = Session(
            title=data.title,
            provider_id=data.provider_id,
            model=data.model,
            system_prompt=data.system_prompt,
            temperature=Decimal(str(data.temperature)) if data.temperature is not None else None,
            max_tokens=data.max_tokens,
            enabled_tools=json.dumps(data.enabled_tools) if data.enabled_tools else json.dumps(["web_search", "db_query"]),
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: Session UUID.

        Returns:
            Session object or None.
        """
        result = await self.db.execute(
            select(Session).where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        provider_id: Optional[str] = None
    ) -> tuple[List[Session], int]:
        """
        Get list of sessions with pagination.

        Args:
            skip: Number of sessions to skip.
            limit: Maximum number of sessions to return.
            provider_id: Filter by provider ID.

        Returns:
            Tuple of (sessions list, total count).
        """
        query = select(Session)

        if provider_id:
            query = query.where(Session.provider_id == provider_id)

        # Get total count
        count_query = select(func.count(Session.id))
        if provider_id:
            count_query = count_query.where(Session.provider_id == provider_id)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Session.updated_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        sessions = list(result.scalars().all())

        return sessions, total

    async def update(self, session_id: str, data: SessionUpdate) -> Optional[Session]:
        """
        Update a session.

        Args:
            session_id: Session UUID.
            data: Session update data.

        Returns:
            Updated Session object or None.
        """
        session = await self.get(session_id)
        if not session:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "temperature" and value is not None:
                value = Decimal(str(value))
            elif key == "enabled_tools" and value is not None:
                value = json.dumps(value)
            setattr(session, key, value)

        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def delete(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session UUID.

        Returns:
            True if deleted, False if not found.
        """
        session = await self.get(session_id)
        if not session:
            return False

        await self.db.delete(session)
        await self.db.flush()
        return True

    async def get_with_messages(self, session_id: str) -> Optional[Session]:
        """
        Get a session with its messages loaded.

        Args:
            session_id: Session UUID.

        Returns:
            Session with messages or None.
        """
        result = await self.db.execute(
            select(Session)
            .options(selectinload(Session.messages))
            .where(Session.id == session_id)
        )
        return result.scalar_one_or_none()

    def to_response(self, session: Session) -> dict:
        """
        Convert a Session model to response dict.

        Args:
            session: Session model.

        Returns:
            Dictionary for response.
        """
        enabled_tools = []
        if session.enabled_tools:
            if isinstance(session.enabled_tools, str):
                enabled_tools = json.loads(session.enabled_tools)
            else:
                enabled_tools = list(session.enabled_tools)

        return {
            "id": str(session.id),
            "title": session.title,
            "provider_id": session.provider_id,
            "model": session.model,
            "system_prompt": session.system_prompt,
            "temperature": float(session.temperature) if session.temperature is not None else None,
            "max_tokens": session.max_tokens,
            "enabled_tools": enabled_tools,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }
