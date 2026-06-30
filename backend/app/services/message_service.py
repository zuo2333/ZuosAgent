"""
Message service for managing chat messages.
"""
import json
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Message
from app.schemas.api import MessageCreate


class MessageService:
    """Service for managing chat messages."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the message service.

        Args:
            db: AsyncSession for database operations.
        """
        self.db = db

    async def create(
        self,
        session_id: str,
        data: MessageCreate
    ) -> Message:
        """
        Create a new message.

        Args:
            session_id: Session UUID.
            data: Message creation data.

        Returns:
            Created Message object.
        """
        message = Message(
            session_id=session_id,
            role=data.role,
            content=data.content,
            tool_calls=data.tool_calls,
            tool_call_id=data.tool_call_id,
        )
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def get(self, message_id: str) -> Optional[Message]:
        """
        Get a message by ID.

        Args:
            message_id: Message UUID.

        Returns:
            Message object or None.
        """
        result = await self.db.execute(
            select(Message).where(Message.id == message_id)
        )
        return result.scalar_one_or_none()

    async def get_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 50,
        role: Optional[str] = None
    ) -> tuple[List[Message], int]:
        """
        Get messages for a session with pagination.

        Args:
            session_id: Session UUID.
            skip: Number of messages to skip.
            limit: Maximum number of messages to return.
            role: Filter by role.

        Returns:
            Tuple of (messages list, total count).
        """
        query = select(Message).where(Message.session_id == session_id)

        if role:
            query = query.where(Message.role == role)

        # Get total count
        count_query = select(func.count(Message.id)).where(Message.session_id == session_id)
        if role:
            count_query = count_query.where(Message.role == role)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Message.created_at.asc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        messages = list(result.scalars().all())

        return messages, total

    async def delete(self, message_id: str) -> bool:
        """
        Delete a message.

        Args:
            message_id: Message UUID.

        Returns:
            True if deleted, False if not found.
        """
        message = await self.get(message_id)
        if not message:
            return False

        await self.db.delete(message)
        await self.db.flush()
        return True

    async def delete_by_session(self, session_id: str) -> int:
        """
        Delete all messages for a session.

        Args:
            session_id: Session UUID.

        Returns:
            Number of messages deleted.
        """
        result = await self.db.execute(
            select(Message).where(Message.session_id == session_id)
        )
        messages = list(result.scalars().all())
        count = len(messages)

        for message in messages:
            await self.db.delete(message)

        await self.db.flush()
        return count

    def to_response(self, message: Message) -> dict:
        """
        Convert a Message model to response dict.

        Args:
            message: Message model.

        Returns:
            Dictionary for response.
        """
        return {
            "id": str(message.id),
            "session_id": str(message.session_id),
            "role": message.role,
            "content": message.content,
            "tool_calls": message.tool_calls,
            "tool_call_id": message.tool_call_id,
            "created_at": message.created_at,
        }

    def to_chat_message(self, message: Message) -> dict:
        """
        Convert a Message model to chat message format for providers.

        Args:
            message: Message model.

        Returns:
            Dictionary in chat message format.
        """
        result = {"role": message.role}

        if message.content:
            result["content"] = message.content

        if message.tool_calls:
            # Convert tool_calls to OpenAI format if stored in frontend format
            converted_tool_calls = []
            for tc in message.tool_calls:
                # Check if it's frontend format (has tool_name) or OpenAI format (has function)
                if "tool_name" in tc:
                    # Frontend format -> OpenAI format
                    converted_tool_calls.append({
                        "id": tc.get("id", ""),
                        "type": "function",
                        "function": {
                            "name": tc.get("tool_name", ""),
                            "arguments": json.dumps(tc.get("arguments", {}))
                        }
                    })
                else:
                    # Already OpenAI format
                    converted_tool_calls.append(tc)
            result["tool_calls"] = converted_tool_calls

        if message.tool_call_id:
            result["tool_call_id"] = message.tool_call_id

        return result
