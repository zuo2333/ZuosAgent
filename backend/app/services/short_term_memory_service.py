"""
Short-term memory service for session-level memory management
"""
import json
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Session, Message, ShortTermMemory
from app.core.config import settings


# Compression settings
COMPRESSION_THRESHOLD = 3000  # Token threshold for compression
KEEP_RECENT_MESSAGES = 6     # Number of recent messages to keep


class CompressionResult:
    """Result of compression operation"""
    def __init__(
        self,
        summary: str,
        entities: Dict[str, List[str]],
        pending_tasks: List[Dict[str, Any]],
        compressed_tokens: int
    ):
        self.summary = summary
        self.entities = entities
        self.pending_tasks = pending_tasks
        self.compressed_tokens = compressed_tokens


class ShortTermMemoryService:
    """
    Service for managing short-term memory (session-level memory).
    Handles session summarization, entity extraction, and task tracking.
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        """
        Initialize the short-term memory service.

        Args:
            db: AsyncSession for database operations.
            llm_client: LLM client for generating summaries (optional for testing).
        """
        self.db = db
        self.llm_client = llm_client

    async def get_or_create(self, session_id: str) -> ShortTermMemory:
        """
        Get existing short-term memory or create a new one.

        Args:
            session_id: Session UUID.

        Returns:
            ShortTermMemory object.
        """
        result = await self.db.execute(
            select(ShortTermMemory).where(ShortTermMemory.session_id == session_id)
        )
        memory = result.scalar_one_or_none()

        if memory is None:
            memory = ShortTermMemory(
                session_id=session_id,
                summary=None,
                entities={},
                pending_tasks=[],
                total_tokens=0
            )
            self.db.add(memory)
            await self.db.flush()
            await self.db.refresh(memory)

        return memory

    async def get(self, session_id: str) -> Optional[ShortTermMemory]:
        """
        Get short-term memory for a session.

        Args:
            session_id: Session UUID.

        Returns:
            ShortTermMemory object or None.
        """
        result = await self.db.execute(
            select(ShortTermMemory).where(ShortTermMemory.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        session_id: str,
        summary: Optional[str] = None,
        entities: Optional[Dict[str, List[str]]] = None,
        pending_tasks: Optional[List[Dict[str, Any]]] = None,
        total_tokens: Optional[int] = None
    ) -> Optional[ShortTermMemory]:
        """
        Update short-term memory.

        Args:
            session_id: Session UUID.
            summary: New summary text.
            entities: Updated entities dict.
            pending_tasks: Updated pending tasks list.
            total_tokens: Updated token count.

        Returns:
            Updated ShortTermMemory or None.
        """
        memory = await self.get(session_id)
        if memory is None:
            return None

        if summary is not None:
            memory.summary = summary
        if entities is not None:
            memory.entities = entities
        if pending_tasks is not None:
            memory.pending_tasks = pending_tasks
        if total_tokens is not None:
            memory.total_tokens = total_tokens

        memory.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(memory)
        return memory

    async def update_token_count(self, session_id: str, token_delta: int) -> Optional[ShortTermMemory]:
        """
        Update token count for a session.

        Args:
            session_id: Session UUID.
            token_delta: Number of tokens to add (can be negative).

        Returns:
            Updated ShortTermMemory or None.
        """
        memory = await self.get_or_create(session_id)
        memory.total_tokens += token_delta
        memory.updated_at = datetime.utcnow()
        await self.db.flush()
        return memory

    async def check_compression_needed(self, session_id: str) -> Tuple[bool, int]:
        """
        Check if compression is needed for a session.

        Args:
            session_id: Session UUID.

        Returns:
            Tuple of (needs_compression, current_tokens).
        """
        memory = await self.get_or_create(session_id)
        return memory.total_tokens >= COMPRESSION_THRESHOLD, memory.total_tokens

    async def compress(
        self,
        session_id: str,
        messages: List[Message],
        force: bool = False
    ) -> Optional[CompressionResult]:
        """
        Compress session messages using sliding window + summarization.
        Performs one-shot LLM call for: summary + entities + tasks.

        Args:
            session_id: Session UUID.
            messages: List of messages to potentially compress.
            force: Force compression regardless of threshold.

        Returns:
            CompressionResult if compression occurred, None otherwise.
        """
        if len(messages) <= KEEP_RECENT_MESSAGES:
            return None

        # Split messages into old (to compress) and recent (to keep)
        old_messages = messages[:-KEEP_RECENT_MESSAGES]
        recent_messages = messages[-KEEP_RECENT_MESSAGES:]

        if not old_messages:
            return None

        # Get existing memory
        memory = await self.get_or_create(session_id)
        existing_summary = memory.summary
        existing_entities = memory.entities or {}
        existing_tasks = memory.pending_tasks or []

        # Generate new summary + entities + tasks in one LLM call
        result = await self._generate_summary_entities_tasks(
            old_messages,
            existing_summary,
            existing_entities,
            existing_tasks
        )

        if result is None:
            return None

        # Update memory
        memory.summary = result.summary
        memory.entities = result.entities
        memory.pending_tasks = result.pending_tasks
        # Recalculate token count (summary + recent messages)
        memory.total_tokens = result.compressed_tokens
        memory.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(memory)

        return result

    async def _generate_summary_entities_tasks(
        self,
        messages: List[Message],
        existing_summary: Optional[str],
        existing_entities: Dict[str, List[str]],
        existing_tasks: List[Dict[str, Any]]
    ) -> Optional[CompressionResult]:
        """
        Generate summary, extract entities, and update tasks in one LLM call.

        Args:
            messages: Messages to process.
            existing_summary: Existing summary to merge with.
            existing_entities: Existing entities to merge with.
            existing_tasks: Existing tasks to update.

        Returns:
            CompressionResult or None.
        """
        if not self.llm_client:
            # Fallback: simple concatenation without LLM
            return self._fallback_compression(messages, existing_summary, existing_entities)

        # Format messages for LLM
        messages_text = self._format_messages_for_llm(messages)

        # Build prompt
        prompt = self._build_compression_prompt(
            messages_text,
            existing_summary,
            existing_entities,
            existing_tasks
        )

        try:
            # Call LLM
            response = await self._call_llm(prompt)

            # Parse response
            result = self._parse_compression_response(response)

            # Calculate token estimate
            compressed_tokens = len(result.summary.split()) * 2  # Rough estimate

            return CompressionResult(
                summary=result.summary,
                entities=result.entities,
                pending_tasks=result.pending_tasks,
                compressed_tokens=compressed_tokens
            )
        except Exception as e:
            # Fallback on error
            return self._fallback_compression(messages, existing_summary, existing_entities)

    def _format_messages_for_llm(self, messages: List[Message]) -> str:
        """Format messages for LLM input."""
        lines = []
        for msg in messages:
            role = msg.role
            content = msg.content or ""
            if len(content) > 500:
                content = content[:500] + "..."
            lines.append(f"[{role}]: {content}")
        return "\n".join(lines)

    def _build_compression_prompt(
        self,
        messages_text: str,
        existing_summary: Optional[str],
        existing_entities: Dict[str, List[str]],
        existing_tasks: List[Dict[str, Any]]
    ) -> str:
        """Build the compression prompt for LLM."""
        prompt = """分析以下对话内容，输出：
1. 摘要：压缩主要内容和结论（2-3 句话，保留关键信息）
2. 实体：提取人物、项目、技术等关键实体（JSON格式）
3. 任务：识别待办事项和当前目标（JSON格式）

"""
        if existing_summary:
            prompt += f"已有摘要：{existing_summary}\n\n请合并新旧信息生成更新后的摘要。\n\n"

        if existing_entities:
            prompt += f"已有实体：{json.dumps(existing_entities, ensure_ascii=False)}\n\n请合并新发现的实体。\n\n"

        if existing_tasks:
            prompt += f"已有任务：{json.dumps(existing_tasks, ensure_ascii=False)}\n\n请更新任务状态。\n\n"

        prompt += f"""对话内容：
{messages_text}

请按以下JSON格式输出（不要包含其他内容）：
{{
    "summary": "更新后的摘要内容",
    "entities": {{
        "persons": ["人物名"],
        "projects": ["项目名"],
        "technologies": ["技术名"],
        "other": ["其他实体"]
    }},
    "pending_tasks": [
        {{"task": "任务描述", "status": "pending|in_progress|completed"}}
    ]
}}"""
        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """Call the LLM with the given prompt."""
        if hasattr(self.llm_client, 'chat'):
            # OpenAI-style client
            response = await self.llm_client.chat.completions.create(
                model="gpt-4o-mini",  # Use efficient model for compression
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content
        else:
            raise ValueError("Invalid LLM client")

    def _parse_compression_response(self, response: str) -> CompressionResult:
        """Parse LLM response into CompressionResult."""
        # Try to extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                data = json.loads(json_match.group())
                return CompressionResult(
                    summary=data.get("summary", ""),
                    entities=data.get("entities", {}),
                    pending_tasks=data.get("pending_tasks", []),
                    compressed_tokens=0
                )
            except json.JSONDecodeError:
                pass

        # Fallback: use entire response as summary
        return CompressionResult(
            summary=response,
            entities={},
            pending_tasks=[],
            compressed_tokens=len(response.split()) * 2
        )

    def _fallback_compression(
        self,
        messages: List[Message],
        existing_summary: Optional[str],
        existing_entities: Dict[str, List[str]]
    ) -> CompressionResult:
        """Fallback compression without LLM."""
        # Simple concatenation of content
        contents = []
        for msg in messages:
            if msg.content:
                contents.append(f"[{msg.role}]: {msg.content[:200]}")

        new_summary = "\n".join(contents[-5:])  # Last 5 exchanges

        if existing_summary:
            new_summary = f"{existing_summary}\n\n{new_summary}"

        return CompressionResult(
            summary=new_summary[:1000],  # Limit length
            entities=existing_entities,
            pending_tasks=[],
            compressed_tokens=len(new_summary.split()) * 2
        )

    async def add_task(
        self,
        session_id: str,
        task: str,
        status: str = "pending"
    ) -> Optional[ShortTermMemory]:
        """
        Add a pending task to the session.

        Args:
            session_id: Session UUID.
            task: Task description.
            status: Task status (pending, in_progress, completed).

        Returns:
            Updated ShortTermMemory or None.
        """
        memory = await self.get_or_create(session_id)

        tasks = list(memory.pending_tasks or [])
        tasks.append({
            "task": task,
            "status": status,
            "created_at": datetime.utcnow().isoformat()
        })
        memory.pending_tasks = tasks
        memory.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(memory)
        return memory

    async def update_task_status(
        self,
        session_id: str,
        task_index: int,
        status: str
    ) -> Optional[ShortTermMemory]:
        """
        Update the status of a pending task.

        Args:
            session_id: Session UUID.
            task_index: Index of the task to update.
            status: New status.

        Returns:
            Updated ShortTermMemory or None.
        """
        memory = await self.get(session_id)
        if memory is None or not memory.pending_tasks:
            return None

        tasks = list(memory.pending_tasks)
        if task_index < 0 or task_index >= len(tasks):
            return None

        tasks[task_index]["status"] = status
        memory.pending_tasks = tasks
        memory.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(memory)
        return memory

    def to_response(self, memory: ShortTermMemory) -> dict:
        """
        Convert ShortTermMemory to response dict.

        Args:
            memory: ShortTermMemory model.

        Returns:
            Dictionary for response.
        """
        return {
            "session_id": str(memory.session_id),
            "summary": memory.summary,
            "entities": memory.entities or {},
            "pending_tasks": memory.pending_tasks or [],
            "total_tokens": memory.total_tokens,
            "created_at": memory.created_at,
            "updated_at": memory.updated_at,
        }
