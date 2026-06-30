"""
Memory integration helpers for chat API
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.memory_context_service import MemoryContextService
from app.services.short_term_memory_service import ShortTermMemoryService
from app.services.long_term_memory_service import LongTermMemoryService
from app.services.user_profile_service import UserProfileService
from app.models import Message


# Default user ID for single-user scenarios
DEFAULT_USER_ID = "default"


class MemoryIntegration:
    """
    Helper class for integrating memory into the chat flow.
    Handles memory injection, token tracking, and extraction triggers.
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        self.db = db
        self.llm_client = llm_client
        self._context_service = None

    @property
    def context_service(self) -> MemoryContextService:
        if self._context_service is None:
            self._context_service = MemoryContextService(self.db, self.llm_client)
        return self._context_service

    async def inject_memory_context(
        self,
        session_id: str,
        user_message: str,
        base_system_prompt: str,
        user_id: str = DEFAULT_USER_ID
    ) -> str:
        """
        Inject memory context into system prompt based on query intent.

        Args:
            session_id: Session UUID.
            user_message: User's input message.
            base_system_prompt: Base system prompt.
            user_id: User identifier.

        Returns:
            System prompt with memory context injected.
        """
        if not settings.MEMORY_ENABLED:
            return base_system_prompt

        # Build memory context based on intent
        memory_context, metadata = await self.context_service.build_context(
            user_id=user_id,
            session_id=session_id,
            query=user_message
        )

        if not memory_context:
            return base_system_prompt

        # Render system prompt with memory context
        return self.context_service.render_system_prompt(
            base_prompt=base_system_prompt,
            memory_context=memory_context
        )

    async def update_token_count(
        self,
        session_id: str,
        token_delta: int
    ) -> None:
        """
        Update token count for a session.

        Args:
            session_id: Session UUID.
            token_delta: Tokens to add.
        """
        if not settings.MEMORY_ENABLED:
            return

        service = ShortTermMemoryService(self.db)
        await service.update_token_count(session_id, token_delta)

    async def check_checkpoint_trigger(
        self,
        session_id: str,
        message_count: int
    ) -> bool:
        """
        Check if checkpoint trigger is needed.

        Args:
            session_id: Session UUID.
            message_count: Current message count.

        Returns:
            True if checkpoint should be triggered.
        """
        if not settings.MEMORY_ENABLED:
            return False

        interval = settings.MEMORY_CHECKPOINT_INTERVAL
        return message_count > 0 and message_count % interval == 0

    async def trigger_memory_extraction(
        self,
        user_id: str,
        session_id: str,
        messages: List[Message],
        user_id_param: str = DEFAULT_USER_ID
    ) -> Dict[str, Any]:
        """
        Trigger memory extraction for a session.
        Called at session end or checkpoint.

        Args:
            user_id: User identifier (unused, for compatibility).
            session_id: Session UUID.
            messages: Session messages.
            user_id_param: User ID parameter.

        Returns:
            Extraction result.
        """
        if not settings.MEMORY_ENABLED:
            return {"extracted": 0}

        # Extract long-term memories
        ltm_service = LongTermMemoryService(self.db, self.llm_client)
        memories = await ltm_service.extract_from_session(
            user_id=user_id_param,
            session_id=session_id,
            messages=messages
        )

        # Update user profile from session
        profile_service = UserProfileService(self.db, self.llm_client)
        await profile_service.update_from_session(
            user_id=user_id_param,
            session=None,  # Not needed for basic update
            messages=messages
        )

        return {
            "extracted": len(memories),
            "memory_ids": [str(m.id) for m in memories]
        }

    async def handle_session_end(
        self,
        user_id: str,
        session_id: str,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """
        Handle session end - trigger full memory extraction.

        Args:
            user_id: User identifier.
            session_id: Session UUID.
            messages: All session messages.

        Returns:
            Extraction result.
        """
        return await self.trigger_memory_extraction(
            user_id=user_id,
            session_id=session_id,
            messages=messages
        )

    async def handle_checkpoint(
        self,
        user_id: str,
        session_id: str,
        messages: List[Message]
    ) -> Dict[str, Any]:
        """
        Handle checkpoint - trigger incremental memory extraction.

        Args:
            user_id: User identifier.
            session_id: Session UUID.
            messages: Recent messages.

        Returns:
            Extraction result.
        """
        # For checkpoint, only process recent messages
        recent_messages = messages[-settings.MEMORY_CHECKPOINT_INTERVAL:]

        return await self.trigger_memory_extraction(
            user_id=user_id,
            session_id=session_id,
            messages=recent_messages
        )
