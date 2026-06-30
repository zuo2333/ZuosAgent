"""
Long-term memory service for persistent memory with vector search
"""
import json
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.dialects.postgresql import array

from app.models import LongTermMemory
from app.models.memory import MemoryType
from app.services.embedding_service import get_embedding_service
from app.core.config import settings


# Decay parameters (Ebbinghaus forgetting curve approximation)
DECAY_HALF_LIFE_DAYS = 100  # After 100 days, importance decays to ~63% of original
MIN_EFFECTIVE_IMPORTANCE = 0.1  # Minimum threshold before cleanup


class MemoryExtractionResult:
    """Result of memory extraction from a session"""
    def __init__(
        self,
        memories: List[Dict[str, Any]],
        confidence: float
    ):
        self.memories = memories
        self.confidence = confidence


class LongTermMemoryService:
    """
    Service for managing long-term memory with vector embeddings.
    Supports semantic retrieval, importance scoring, and decay.
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        """
        Initialize the long-term memory service.

        Args:
            db: AsyncSession for database operations.
            llm_client: LLM client for memory extraction (optional).
        """
        self.db = db
        self.llm_client = llm_client
        self._embedding_service = None

    @property
    def embedding_service(self):
        """Lazy load embedding service"""
        if self._embedding_service is None:
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    # ==================== CRUD Operations ====================

    async def create(
        self,
        user_id: str,
        content: str,
        memory_type: MemoryType,
        importance: float = 0.5,
        source_session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LongTermMemory:
        """
        Create a new long-term memory with embedding.

        Args:
            user_id: User identifier.
            content: Memory content text.
            memory_type: Type of memory (fact, preference, event).
            importance: Initial importance score (0-1).
            source_session_id: Session this memory was extracted from.
            metadata: Additional metadata.

        Returns:
            Created LongTermMemory object.
        """
        # Check for duplicates first
        existing = await self.find_similar(user_id, content, threshold=0.85)
        if existing:
            # Update importance instead of creating duplicate
            return await self.update_importance(existing.id, 0.1)  # Boost by 0.1

        # Generate embedding
        embedding = await self.embedding_service.embed(content)

        memory = LongTermMemory(
            user_id=user_id,
            content=content,
            memory_type=memory_type.value,
            embedding=embedding,
            importance=Decimal(str(importance)),
            decay_factor=Decimal("1.0"),
            access_count=0,
            source_session_id=source_session_id,
            extra_data=metadata or {}
        )

        self.db.add(memory)
        await self.db.flush()
        await self.db.refresh(memory)
        return memory

    async def get(self, memory_id: str) -> Optional[LongTermMemory]:
        """
        Get a memory by ID.

        Args:
            memory_id: Memory UUID.

        Returns:
            LongTermMemory object or None.
        """
        result = await self.db.execute(
            select(LongTermMemory).where(LongTermMemory.id == memory_id)
        )
        return result.scalar_one_or_none()

    async def get_by_user(
        self,
        user_id: str,
        memory_types: Optional[List[MemoryType]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[LongTermMemory], int]:
        """
        Get memories for a user with optional type filter.

        Args:
            user_id: User identifier.
            memory_types: Optional list of memory types to filter.
            skip: Number of memories to skip.
            limit: Maximum number to return.

        Returns:
            Tuple of (memories list, total count).
        """
        query = select(LongTermMemory).where(LongTermMemory.user_id == user_id)

        if memory_types:
            type_values = [t.value for t in memory_types]
            query = query.where(LongTermMemory.memory_type.in_(type_values))

        # Get total count
        count_query = select(func.count(LongTermMemory.id)).where(
            LongTermMemory.user_id == user_id
        )
        if memory_types:
            count_query = count_query.where(LongTermMemory.memory_type.in_(type_values))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(LongTermMemory.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        memories = list(result.scalars().all())

        return memories, total

    async def delete(self, memory_id: str) -> bool:
        """
        Delete a memory.

        Args:
            memory_id: Memory UUID.

        Returns:
            True if deleted, False if not found.
        """
        memory = await self.get(memory_id)
        if not memory:
            return False

        await self.db.delete(memory)
        await self.db.flush()
        return True

    # ==================== Vector Search ====================

    async def search(
        self,
        user_id: str,
        query: str,
        top_k: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        min_importance: Optional[float] = None
    ) -> List[Tuple[LongTermMemory, float]]:
        """
        Search memories by semantic similarity.

        Args:
            user_id: User identifier.
            query: Search query text.
            top_k: Maximum number of results.
            memory_types: Optional type filter.
            min_importance: Minimum importance threshold.

        Returns:
            List of (memory, similarity) tuples.
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.embed(query)

        # Build base query
        base_query = select(LongTermMemory).where(LongTermMemory.user_id == user_id)

        if memory_types:
            type_values = [t.value for t in memory_types]
            base_query = base_query.where(LongTermMemory.memory_type.in_(type_values))

        if min_importance is not None:
            base_query = base_query.where(
                LongTermMemory.importance >= min_importance
            )

        # Execute query
        result = await self.db.execute(base_query)
        memories = list(result.scalars().all())

        # Calculate similarities and sort
        similarities = []
        for memory in memories:
            if memory.embedding:
                similarity = self._cosine_similarity(query_embedding, memory.embedding)
                # Apply decay factor to ranking
                effective_sim = similarity * float(memory.decay_factor) * float(memory.importance)
                similarities.append((memory, effective_sim, similarity))

        # Sort by effective similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        results = []
        for memory, effective_sim, raw_sim in similarities[:top_k]:
            results.append((memory, raw_sim))
            # Update access stats
            await self._update_access_stats(memory)

        return results

    async def find_similar(
        self,
        user_id: str,
        content: str,
        threshold: float = 0.85
    ) -> Optional[LongTermMemory]:
        """
        Find a similar existing memory.

        Args:
            user_id: User identifier.
            content: Content to compare.
            threshold: Similarity threshold.

        Returns:
            Similar memory or None.
        """
        results = await self.search(user_id, content, top_k=1)
        if results and results[0][1] >= threshold:
            return results[0][0]
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    async def _update_access_stats(self, memory: LongTermMemory) -> None:
        """Update access statistics for a memory."""
        memory.access_count += 1
        memory.last_accessed_at = datetime.utcnow()
        await self.db.flush()

    # ==================== Memory Extraction ====================

    async def extract_from_session(
        self,
        user_id: str,
        session_id: str,
        messages: List[Any],
        short_term_memory: Optional[Any] = None
    ) -> List[LongTermMemory]:
        """
        Extract long-term memories from a session.

        Args:
            user_id: User identifier.
            session_id: Session UUID.
            messages: List of session messages.
            short_term_memory: Optional short-term memory for context.

        Returns:
            List of created LongTermMemory objects.
        """
        if not self.llm_client:
            return []

        # Build extraction prompt
        prompt = self._build_extraction_prompt(messages, short_term_memory)

        try:
            # Call LLM for extraction
            response = await self._call_llm(prompt)

            # Parse extracted memories
            extracted = self._parse_extraction_response(response)

            # Create memories with embeddings
            created_memories = []
            for mem_data in extracted:
                if mem_data.get("confidence", 0) >= 0.7:  # Confidence threshold
                    memory = await self.create(
                        user_id=user_id,
                        content=mem_data["content"],
                        memory_type=MemoryType(mem_data.get("type", "fact")),
                        importance=mem_data.get("importance", 0.5),
                        source_session_id=session_id,
                        metadata={"confidence": mem_data.get("confidence")}
                    )
                    created_memories.append(memory)

            return created_memories
        except Exception as e:
            return []

    def _build_extraction_prompt(
        self,
        messages: List[Any],
        short_term_memory: Optional[Any]
    ) -> str:
        """Build the memory extraction prompt."""
        # Format messages
        messages_text = ""
        for msg in messages:
            role = getattr(msg, 'role', 'unknown')
            content = getattr(msg, 'content', '') or ""
            if len(content) > 300:
                content = content[:300] + "..."
            messages_text += f"[{role}]: {content}\n"

        prompt = f"""分析以下对话，提取值得长期记忆的信息。

对话内容：
{messages_text}

请提取以下类型的记忆：
1. **事实** (fact)：用户陈述的个人信息、工作、偏好等
2. **偏好** (preference)：用户明确表达的喜好或习惯
3. **事件** (event)：重要的交互事件、完成的任务等

对于每条记忆，评估：
- 内容：简洁描述记忆内容
- 类型：fact/preference/event
- 重要性：0-1 之间的分数
- 置信度：0-1 之间的分数（>=0.7 才会存储）

请按JSON格式输出（不要包含其他内容）：
{{
    "memories": [
        {{
            "content": "记忆内容描述",
            "type": "fact",
            "importance": 0.8,
            "confidence": 0.9
        }}
    ]
}}"""
        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if hasattr(self.llm_client, 'chat'):
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        raise ValueError("Invalid LLM client")

    def _parse_extraction_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM extraction response."""
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return data.get("memories", [])
            except json.JSONDecodeError:
                pass
        return []

    # ==================== Importance & Decay ====================

    async def update_importance(
        self,
        memory_id: str,
        delta: float
    ) -> Optional[LongTermMemory]:
        """
        Update importance score for a memory.

        Args:
            memory_id: Memory UUID.
            delta: Amount to add to importance (can be negative).

        Returns:
            Updated memory or None.
        """
        memory = await self.get(memory_id)
        if not memory:
            return None

        new_importance = float(memory.importance) + delta
        memory.importance = Decimal(str(max(0.0, min(1.0, new_importance))))
        memory.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(memory)
        return memory

    async def apply_decay(self, user_id: Optional[str] = None) -> int:
        """
        Apply time-based decay to memory importance.
        Called periodically to implement forgetting curve.

        Args:
            user_id: Optional user to limit decay scope.

        Returns:
            Number of memories updated.
        """
        query = select(LongTermMemory)
        if user_id:
            query = query.where(LongTermMemory.user_id == user_id)

        result = await self.db.execute(query)
        memories = list(result.scalars().all())

        now = datetime.utcnow()
        updated_count = 0

        for memory in memories:
            days_old = (now - memory.created_at).days

            # Exponential decay: decay_factor = e^(-days / half_life)
            decay_rate = math.log(2) / DECAY_HALF_LIFE_DAYS
            new_decay = math.exp(-days_old * decay_rate)

            memory.decay_factor = Decimal(str(new_decay))
            updated_count += 1

        await self.db.flush()
        return updated_count

    async def cleanup_low_importance(
        self,
        user_id: Optional[str] = None,
        threshold: float = MIN_EFFECTIVE_IMPORTANCE
    ) -> int:
        """
        Remove memories with very low effective importance.

        Args:
            user_id: Optional user to limit cleanup scope.
            threshold: Minimum effective importance to keep.

        Returns:
            Number of memories removed.
        """
        query = select(LongTermMemory)
        if user_id:
            query = query.where(LongTermMemory.user_id == user_id)

        result = await self.db.execute(query)
        memories = list(result.scalars().all())

        removed_count = 0
        for memory in memories:
            effective = float(memory.importance) * float(memory.decay_factor)
            if effective < threshold:
                await self.db.delete(memory)
                removed_count += 1

        await self.db.flush()
        return removed_count

    # ==================== Statistics ====================

    async def get_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get memory statistics for a user.

        Args:
            user_id: User identifier.

        Returns:
            Statistics dictionary.
        """
        # Total count
        total_result = await self.db.execute(
            select(func.count(LongTermMemory.id)).where(
                LongTermMemory.user_id == user_id
            )
        )
        total = total_result.scalar()

        # By type
        type_result = await self.db.execute(
            select(
                LongTermMemory.memory_type,
                func.count(LongTermMemory.id)
            ).where(
                LongTermMemory.user_id == user_id
            ).group_by(LongTermMemory.memory_type)
        )
        by_type = {row[0]: row[1] for row in type_result}

        # Average importance
        avg_result = await self.db.execute(
            select(func.avg(LongTermMemory.importance)).where(
                LongTermMemory.user_id == user_id
            )
        )
        avg_importance = float(avg_result.scalar() or 0)

        # Total access count
        access_result = await self.db.execute(
            select(func.sum(LongTermMemory.access_count)).where(
                LongTermMemory.user_id == user_id
            )
        )
        total_access = int(access_result.scalar() or 0)

        # Date range
        oldest_result = await self.db.execute(
            select(func.min(LongTermMemory.created_at)).where(
                LongTermMemory.user_id == user_id
            )
        )
        oldest = oldest_result.scalar()

        newest_result = await self.db.execute(
            select(func.max(LongTermMemory.created_at)).where(
                LongTermMemory.user_id == user_id
            )
        )
        newest = newest_result.scalar()

        return {
            "total_memories": total,
            "by_type": by_type,
            "avg_importance": round(avg_importance, 3),
            "total_access_count": total_access,
            "oldest_memory": oldest,
            "newest_memory": newest
        }

    def to_response(self, memory: LongTermMemory) -> dict:
        """Convert LongTermMemory to response dict."""
        return {
            "id": str(memory.id),
            "user_id": memory.user_id,
            "content": memory.content,
            "memory_type": memory.memory_type,
            "importance": float(memory.importance),
            "decay_factor": float(memory.decay_factor),
            "access_count": memory.access_count,
            "last_accessed_at": memory.last_accessed_at,
            "source_session_id": str(memory.source_session_id) if memory.source_session_id else None,
            "metadata": memory.extra_data or {},
            "created_at": memory.created_at,
            "updated_at": memory.updated_at,
        }
