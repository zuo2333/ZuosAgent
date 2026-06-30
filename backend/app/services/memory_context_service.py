"""
Memory context service for integrating all memory layers
"""
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.short_term_memory_service import ShortTermMemoryService
from app.services.long_term_memory_service import LongTermMemoryService
from app.services.user_profile_service import UserProfileService
from app.models.memory import MemoryType
from app.core.config import settings


class MemoryIntent:
    """Memory injection intent classification"""
    NONE = "none"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    BOTH = "both"


class MemoryIntentClassifier:
    """
    Rule-based classifier for memory injection intent.
    No LLM calls - uses pattern matching only.
    """

    # Patterns that indicate NO memory needed
    NO_MEMORY_PATTERNS = [
        r'^(你好|hi|hello|hey)[\s!！.。]*$',
        r'^(谢谢|thanks|thank you)[\s!！.。]*$',
        r'^(好的|ok|okay|嗯|嗯嗯)[\s!！.。]*$',
        r'^(再见|bye|goodbye)[\s!！.。]*$',
        r'^(什么是|解释一下|什么是)',
        r'^(如何|怎么|怎样)',
        r'^(写一个|生成|创建)',
    ]

    # Patterns that indicate SHORT-TERM memory needed
    SHORT_TERM_PATTERNS = [
        r'(刚才|刚刚|之前说的|上面提到|之前聊)',
        r'(继续|接着|下一步|接下来)',
        r'(我们讨论|我们说|我们聊)',
        r'(上一个问题|刚才的问题)',
        r'(回到|回到刚才)',
    ]

    # Patterns that indicate LONG-TERM memory needed
    LONG_TERM_PATTERNS = [
        r'(上次|以前|之前|曾经|往期)',
        r'(我的偏好|我喜欢|我不喜欢|我讨厌)',
        r'(记住|别忘了|记得)',
        r'(那个项目|那个问题)',
        r'(历史|过去的)',
        r'(我的信息|我的资料)',
    ]

    def classify(self, query: str) -> str:
        """
        Classify the memory intent for a query.

        Args:
            query: User input text.

        Returns:
            Intent: "none", "short_term", "long_term", or "both"
        """
        query_lower = query.lower().strip()

        # Check for no-memory patterns first
        for pattern in self.NO_MEMORY_PATTERNS:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return MemoryIntent.NONE

        needs_short = False
        needs_long = False

        # Check short-term patterns
        for pattern in self.SHORT_TERM_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                needs_short = True
                break

        # Check long-term patterns
        for pattern in self.LONG_TERM_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                needs_long = True
                break

        # Determine result
        if needs_short and needs_long:
            return MemoryIntent.BOTH
        elif needs_short:
            return MemoryIntent.SHORT_TERM
        elif needs_long:
            return MemoryIntent.LONG_TERM
        else:
            # Default: no explicit memory signals
            return MemoryIntent.NONE


class MemoryContextService:
    """
    Service for integrating all memory layers and formatting context for LLM.
    Coordinates short-term memory, long-term memory, and user profile.
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        """
        Initialize the memory context service.

        Args:
            db: AsyncSession for database operations.
            llm_client: LLM client for memory operations (optional).
        """
        self.db = db
        self.llm_client = llm_client
        self._short_term_service = None
        self._long_term_service = None
        self._profile_service = None
        self._intent_classifier = MemoryIntentClassifier()

    @property
    def short_term_service(self) -> ShortTermMemoryService:
        if self._short_term_service is None:
            self._short_term_service = ShortTermMemoryService(self.db, self.llm_client)
        return self._short_term_service

    @property
    def long_term_service(self) -> LongTermMemoryService:
        if self._long_term_service is None:
            self._long_term_service = LongTermMemoryService(self.db, self.llm_client)
        return self._long_term_service

    @property
    def profile_service(self) -> UserProfileService:
        if self._profile_service is None:
            self._profile_service = UserProfileService(self.db, self.llm_client)
        return self._profile_service

    # ==================== Intent Classification ====================

    def classify_intent(self, query: str) -> str:
        """
        Classify memory injection intent for a query.

        Args:
            query: User input text.

        Returns:
            Intent classification string.
        """
        return self._intent_classifier.classify(query)

    # ==================== Context Building ====================

    async def build_context(
        self,
        user_id: str,
        session_id: str,
        query: str,
        token_budget: int = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Build memory context for LLM injection based on query intent.

        Args:
            user_id: User identifier.
            session_id: Session UUID.
            query: User input text.
            token_budget: Maximum tokens for context (default from settings).

        Returns:
            Tuple of (formatted_context, metadata).
        """
        if token_budget is None:
            token_budget = settings.MEMORY_TOKEN_BUDGET

        # Classify intent
        intent = self.classify_intent(query)

        metadata = {
            "intent": intent,
            "user_profile_included": False,
            "long_term_included": False,
            "short_term_included": False,
            "tokens_used": 0
        }

        if intent == MemoryIntent.NONE:
            return "", metadata

        parts = []
        tokens_used = 0

        # Always include user profile (small)
        profile = await self.profile_service.get_or_create(user_id)
        profile_text = self.profile_service.format_for_context(profile)
        profile_tokens = self._estimate_tokens(profile_text)
        if tokens_used + profile_tokens <= token_budget:
            parts.append(profile_text)
            tokens_used += profile_tokens
            metadata["user_profile_included"] = True

        # Include short-term memory if needed
        if intent in [MemoryIntent.SHORT_TERM, MemoryIntent.BOTH]:
            stm = await self.short_term_service.get(session_id)
            if stm:
                stm_text = self._format_short_term_memory(stm)
                stm_tokens = self._estimate_tokens(stm_text)
                if tokens_used + stm_tokens <= token_budget:
                    parts.append(stm_text)
                    tokens_used += stm_tokens
                    metadata["short_term_included"] = True

        # Include long-term memory if needed
        if intent in [MemoryIntent.LONG_TERM, MemoryIntent.BOTH]:
            ltm_results = await self.long_term_service.search(
                user_id=user_id,
                query=query,
                top_k=5
            )
            if ltm_results:
                ltm_text = self._format_long_term_memories(ltm_results)
                ltm_tokens = self._estimate_tokens(ltm_text)
                if tokens_used + ltm_tokens <= token_budget:
                    parts.append(ltm_text)
                    tokens_used += ltm_tokens
                    metadata["long_term_included"] = True

        metadata["tokens_used"] = tokens_used

        context = "\n\n".join(parts)
        return context, metadata

    async def get_full_context(
        self,
        user_id: str,
        session_id: str,
        include_profile: bool = True,
        include_long_term: bool = True,
        include_short_term: bool = True,
        long_term_query: str = None,
        token_budget: int = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Get full memory context without intent filtering.
        Used for explicit memory requests.

        Args:
            user_id: User identifier.
            session_id: Session UUID.
            include_profile: Include user profile.
            include_long_term: Include long-term memories.
            include_short_term: Include short-term memory.
            long_term_query: Query for long-term memory search.
            token_budget: Maximum tokens for context.

        Returns:
            Tuple of (formatted_context, metadata).
        """
        if token_budget is None:
            token_budget = settings.MEMORY_TOKEN_BUDGET

        parts = []
        tokens_used = 0
        metadata = {
            "user_profile_included": False,
            "long_term_included": False,
            "short_term_included": False,
            "tokens_used": 0
        }

        # User profile
        if include_profile:
            profile = await self.profile_service.get_or_create(user_id)
            profile_text = self.profile_service.format_for_context(profile)
            profile_tokens = self._estimate_tokens(profile_text)
            if tokens_used + profile_tokens <= token_budget:
                parts.append(profile_text)
                tokens_used += profile_tokens
                metadata["user_profile_included"] = True

        # Short-term memory
        if include_short_term:
            stm = await self.short_term_service.get(session_id)
            if stm:
                stm_text = self._format_short_term_memory(stm)
                stm_tokens = self._estimate_tokens(stm_text)
                if tokens_used + stm_tokens <= token_budget:
                    parts.append(stm_text)
                    tokens_used += stm_tokens
                    metadata["short_term_included"] = True

        # Long-term memory
        if include_long_term:
            query = long_term_query or ""
            ltm_results = await self.long_term_service.search(
                user_id=user_id,
                query=query,
                top_k=10
            )
            if ltm_results:
                ltm_text = self._format_long_term_memories(ltm_results)
                ltm_tokens = self._estimate_tokens(ltm_text)
                remaining_budget = token_budget - tokens_used
                if ltm_tokens > remaining_budget:
                    # Truncate to fit budget
                    ltm_text = ltm_text[:remaining_budget * 4]
                    ltm_tokens = self._estimate_tokens(ltm_text)
                parts.append(ltm_text)
                tokens_used += ltm_tokens
                metadata["long_term_included"] = True

        metadata["tokens_used"] = tokens_used
        context = "\n\n".join(parts)
        return context, metadata

    # ==================== Formatting ====================

    def _format_short_term_memory(self, memory) -> str:
        """Format short-term memory for context."""
        lines = ["## 当前会话状态"]

        if memory.summary:
            lines.append(f"- 摘要: {memory.summary[:500]}")

        entities = memory.entities or {}
        if entities:
            entity_parts = []
            for category, items in entities.items():
                if items:
                    entity_parts.append(f"{category}: {', '.join(items[:5])}")
            if entity_parts:
                lines.append(f"- 实体: {'; '.join(entity_parts)}")

        tasks = memory.pending_tasks or []
        active_tasks = [t for t in tasks if t.get("status") != "completed"]
        if active_tasks:
            task_list = [t.get("task", "") for t in active_tasks[:3]]
            lines.append(f"- 待办: {', '.join(task_list)}")

        return "\n".join(lines)

    def _format_long_term_memories(
        self,
        memories: List[Tuple[Any, float]]
    ) -> str:
        """Format long-term memories for context."""
        lines = ["## 相关记忆"]

        type_labels = {
            "fact": "事实",
            "preference": "偏好",
            "event": "事件"
        }

        for memory, similarity in memories[:10]:
            type_label = type_labels.get(memory.memory_type, memory.memory_type)
            lines.append(f"- [{type_label}] {memory.content}")

        return "\n".join(lines)

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough: 1 token ≈ 4 chars for Chinese)."""
        if not text:
            return 0
        # Rough estimation: Chinese chars ~0.5 tokens, English words ~1 token
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        other_chars = len(text) - chinese_chars
        return chinese_chars // 2 + other_chars // 4 + 1

    # ==================== System Prompt Template ====================

    def render_system_prompt(
        self,
        base_prompt: str,
        memory_context: str
    ) -> str:
        """
        Render system prompt with memory context.

        Args:
            base_prompt: Base system prompt.
            memory_context: Formatted memory context.

        Returns:
            Complete system prompt.
        """
        if not memory_context:
            return base_prompt

        template = f"""{base_prompt}

---

以下是与本次对话相关的背景信息，请在回复时参考：

{memory_context}
"""
        return template
