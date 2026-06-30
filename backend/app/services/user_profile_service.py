"""
User profile service for managing user preferences and behavior patterns
"""
import json
import re
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import UserProfile
from app.core.config import settings


# Default user ID for single-user scenarios
DEFAULT_USER_ID = "default"


class UserProfileService:
    """
    Service for managing user profiles.
    Handles preferences, behavior analysis, and knowledge graph.
    """

    def __init__(self, db: AsyncSession, llm_client=None):
        """
        Initialize the user profile service.

        Args:
            db: AsyncSession for database operations.
            llm_client: LLM client for profile inference (optional).
        """
        self.db = db
        self.llm_client = llm_client

    # ==================== CRUD Operations ====================

    async def get_or_create(self, user_id: str = DEFAULT_USER_ID) -> UserProfile:
        """
        Get existing profile or create a default one.

        Args:
            user_id: User identifier.

        Returns:
            UserProfile object.
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if profile is None:
            profile = UserProfile(
                user_id=user_id,
                nickname=None,
                language="zh-CN",
                response_style={"verbosity": "normal"},
                tech_level="intermediate",
                interests=[],
                task_distribution={},
                active_hours={},
                tool_usage={},
                knowledge_graph={"entities": [], "relations": []},
                profile_version=1
            )
            self.db.add(profile)
            await self.db.flush()
            await self.db.refresh(profile)

        return profile

    async def get(self, user_id: str = DEFAULT_USER_ID) -> Optional[UserProfile]:
        """
        Get user profile.

        Args:
            user_id: User identifier.

        Returns:
            UserProfile or None.
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update(
        self,
        user_id: str = DEFAULT_USER_ID,
        nickname: Optional[str] = None,
        language: Optional[str] = None,
        response_style: Optional[Dict[str, Any]] = None,
        tech_level: Optional[str] = None,
        interests: Optional[List[str]] = None
    ) -> Optional[UserProfile]:
        """
        Update user profile fields.

        Args:
            user_id: User identifier.
            nickname: Display name.
            language: Language preference.
            response_style: Response style preferences.
            tech_level: Technical level (beginner/intermediate/expert).
            interests: List of interest areas.

        Returns:
            Updated UserProfile or None.
        """
        profile = await self.get_or_create(user_id)

        if nickname is not None:
            profile.nickname = nickname
        if language is not None:
            profile.language = language
        if response_style is not None:
            current_style = profile.response_style or {}
            current_style.update(response_style)
            profile.response_style = current_style
        if tech_level is not None:
            profile.tech_level = tech_level
        if interests is not None:
            profile.interests = interests

        profile.profile_version += 1
        profile.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    # ==================== Behavior Analysis ====================

    async def update_task_distribution(
        self,
        user_id: str,
        task_type: str,
        count: int = 1
    ) -> Optional[UserProfile]:
        """
        Update task distribution statistics.

        Args:
            user_id: User identifier.
            task_type: Type of task (e.g., "programming", "writing").
            count: Count to add.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        distribution = profile.task_distribution or {}
        distribution[task_type] = distribution.get(task_type, 0) + count
        profile.task_distribution = distribution
        profile.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_active_hours(
        self,
        user_id: str,
        hour: int
    ) -> Optional[UserProfile]:
        """
        Update active hours statistics.

        Args:
            user_id: User identifier.
            hour: Hour of day (0-23).

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        active_hours = profile.active_hours or {}
        hour_str = str(hour)
        active_hours[hour_str] = active_hours.get(hour_str, 0) + 1
        profile.active_hours = active_hours
        profile.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_tool_usage(
        self,
        user_id: str,
        tool_name: str,
        count: int = 1
    ) -> Optional[UserProfile]:
        """
        Update tool usage statistics.

        Args:
            user_id: User identifier.
            tool_name: Name of the tool used.
            count: Count to add.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        tool_usage = profile.tool_usage or {}
        tool_usage[tool_name] = tool_usage.get(tool_name, 0) + count
        profile.tool_usage = tool_usage
        profile.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def update_from_session(
        self,
        user_id: str,
        session: Any,
        messages: List[Any],
        tool_calls: List[Any] = None
    ) -> Optional[UserProfile]:
        """
        Update profile from a completed session.
        Updates task distribution, active hours, and tool usage.

        Args:
            user_id: User identifier.
            session: Session object.
            messages: List of messages in session.
            tool_calls: List of tool calls made.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        # Update active hours based on message timestamps
        for msg in messages:
            msg_hour = msg.created_at.hour
            await self.update_active_hours(user_id, msg_hour)

        # Update tool usage
        if tool_calls:
            for tc in tool_calls:
                await self.update_tool_usage(user_id, tc.tool_name)

        return profile

    # ==================== Knowledge Graph ====================

    async def add_entity(
        self,
        user_id: str,
        entity_id: str,
        name: str,
        entity_type: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[UserProfile]:
        """
        Add an entity to the knowledge graph.

        Args:
            user_id: User identifier.
            entity_id: Unique entity identifier.
            name: Entity name.
            entity_type: Type of entity (person, company, project, etc.).
            attributes: Additional attributes.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        kg = profile.knowledge_graph or {"entities": [], "relations": []}

        # Check if entity already exists
        existing = next(
            (e for e in kg["entities"] if e.get("id") == entity_id),
            None
        )

        if existing:
            # Update existing entity
            existing["name"] = name
            existing["type"] = entity_type
            if attributes:
                existing.setdefault("attributes", {}).update(attributes)
        else:
            # Add new entity
            kg["entities"].append({
                "id": entity_id,
                "name": name,
                "type": entity_type,
                "attributes": attributes or {}
            })

        profile.knowledge_graph = kg
        profile.profile_version += 1
        profile.updated_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(profile)
        return profile

    async def add_relation(
        self,
        user_id: str,
        source_id: str,
        relation: str,
        target_id: str
    ) -> Optional[UserProfile]:
        """
        Add a relation to the knowledge graph.

        Args:
            user_id: User identifier.
            source_id: Source entity ID.
            relation: Relation type (e.g., "works_at", "friend_of").
            target_id: Target entity ID.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        kg = profile.knowledge_graph or {"entities": [], "relations": []}

        # Check if relation already exists
        existing = next(
            (r for r in kg["relations"]
             if r.get("source") == source_id
             and r.get("relation") == relation
             and r.get("target") == target_id),
            None
        )

        if not existing:
            kg["relations"].append({
                "source": source_id,
                "relation": relation,
                "target": target_id
            })
            profile.knowledge_graph = kg
            profile.profile_version += 1
            profile.updated_at = datetime.utcnow()
            await self.db.flush()
            await self.db.refresh(profile)

        return profile

    # ==================== Profile Inference ====================

    async def infer_profile(
        self,
        user_id: str,
        sessions: List[Any],
        force: bool = False
    ) -> Optional[UserProfile]:
        """
        Infer user profile from recent sessions using LLM.

        Args:
            user_id: User identifier.
            sessions: List of recent sessions to analyze.
            force: Force inference even if recently done.

        Returns:
            Updated profile or None.
        """
        profile = await self.get_or_create(user_id)

        # Check frequency control (skip if inferred recently)
        if not force and profile.last_inferred_at:
            time_since_last = datetime.utcnow() - profile.last_inferred_at
            if time_since_last < timedelta(hours=24):
                return profile

        if not self.llm_client or not sessions:
            return profile

        # Build inference prompt
        prompt = self._build_inference_prompt(sessions, profile)

        try:
            response = await self._call_llm(prompt)
            inferred = self._parse_inference_response(response)

            if inferred:
                # Update profile with inferred values
                if inferred.get("tech_level"):
                    profile.tech_level = inferred["tech_level"]
                if inferred.get("interests"):
                    profile.interests = inferred["interests"]
                if inferred.get("response_style"):
                    current_style = profile.response_style or {}
                    current_style.update(inferred["response_style"])
                    profile.response_style = current_style

                profile.last_inferred_at = datetime.utcnow()
                profile.profile_version += 1
                profile.updated_at = datetime.utcnow()

                await self.db.flush()
                await self.db.refresh(profile)

        except Exception:
            pass

        return profile

    def _build_inference_prompt(
        self,
        sessions: List[Any],
        current_profile: UserProfile
    ) -> str:
        """Build the profile inference prompt."""
        # Summarize sessions
        session_summaries = []
        for session in sessions[:5]:  # Last 5 sessions
            title = getattr(session, 'title', 'Untitled')
            session_summaries.append(f"- {title}")

        sessions_text = "\n".join(session_summaries)

        # Current profile state
        current_state = f"""
当前画像状态：
- 技术水平：{current_profile.tech_level}
- 兴趣领域：{json.dumps(current_profile.interests, ensure_ascii=False)}
- 回复偏好：{json.dumps(current_profile.response_style, ensure_ascii=False)}
"""

        prompt = f"""基于以下用户最近的会话历史，推断用户的画像特征。

最近会话：
{sessions_text}

{current_state}

请推断以下信息，仅在有足够证据时更新：
1. 技术水平（beginner/intermediate/expert）
2. 兴趣领域（列表）
3. 回复偏好（verbosity: concise/normal/detailed）

请按JSON格式输出（不要包含其他内容）：
{{
    "tech_level": "intermediate",
    "interests": ["Python", "AI", "Web开发"],
    "response_style": {{"verbosity": "normal"}},
    "reasoning": "推断理由"
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

    def _parse_inference_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse LLM inference response."""
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return None

    # ==================== Response Formatting ====================

    def to_response(self, profile: UserProfile) -> dict:
        """Convert UserProfile to response dict."""
        return {
            "user_id": profile.user_id,
            "nickname": profile.nickname,
            "language": profile.language,
            "response_style": profile.response_style or {"verbosity": "normal"},
            "tech_level": profile.tech_level,
            "interests": profile.interests or [],
            "task_distribution": profile.task_distribution or {},
            "active_hours": profile.active_hours or {},
            "tool_usage": profile.tool_usage or {},
            "knowledge_graph": profile.knowledge_graph or {"entities": [], "relations": []},
            "profile_version": profile.profile_version,
            "last_inferred_at": profile.last_inferred_at,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }

    def format_for_context(self, profile: UserProfile) -> str:
        """
        Format profile for LLM context injection.

        Args:
            profile: UserProfile object.

        Returns:
            Formatted string for context.
        """
        lines = ["## 关于用户"]

        if profile.nickname:
            lines.append(f"- 称呼: {profile.nickname}")

        lines.append(f"- 技术水平: {self._tech_level_cn(profile.tech_level)}")

        # Response style
        style = profile.response_style or {}
        verbosity = style.get("verbosity", "normal")
        verbosity_cn = {"concise": "简洁", "normal": "适中", "detailed": "详细"}.get(verbosity, "适中")
        lines.append(f"- 回复偏好: {verbosity_cn}")

        # Interests
        if profile.interests:
            lines.append(f"- 兴趣领域: {', '.join(profile.interests[:5])}")

        return "\n".join(lines)

    def _tech_level_cn(self, level: str) -> str:
        """Convert tech level to Chinese."""
        mapping = {
            "beginner": "初学者",
            "intermediate": "中级",
            "expert": "专家级"
        }
        return mapping.get(level, level)
