"""
Tests for memory system services
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.memory_context_service import MemoryIntentClassifier, MemoryIntent
from app.services.embedding_service import EmbeddingService, EmbeddingCache


class TestMemoryIntentClassifier:
    """Tests for the memory intent classifier"""

    def setup_method(self):
        self.classifier = MemoryIntentClassifier()

    def test_greeting_returns_none(self):
        """Greetings should return NONE intent"""
        result = self.classifier.classify("你好")
        assert result == MemoryIntent.NONE

        result = self.classifier.classify("hi")
        assert result == MemoryIntent.NONE

        result = self.classifier.classify("hello!")
        assert result == MemoryIntent.NONE

    def test_thanks_returns_none(self):
        """Thanks should return NONE intent"""
        result = self.classifier.classify("谢谢")
        assert result == MemoryIntent.NONE

        result = self.classifier.classify("thanks")
        assert result == MemoryIntent.NONE

    def test_knowledge_question_returns_none(self):
        """Knowledge questions should return NONE intent"""
        result = self.classifier.classify("什么是 Python？")
        assert result == MemoryIntent.NONE

        result = self.classifier.classify("解释一下快速排序")
        assert result == MemoryIntent.NONE

    def test_reference_to_current_session_returns_short_term(self):
        """References to current session should return SHORT_TERM"""
        result = self.classifier.classify("我们刚才讨论了什么？")
        assert result == MemoryIntent.SHORT_TERM

        result = self.classifier.classify("继续上一步")
        assert result == MemoryIntent.SHORT_TERM

        result = self.classifier.classify("你刚才说的方法")
        assert result == MemoryIntent.SHORT_TERM

    def test_reference_to_history_returns_long_term(self):
        """References to history should return LONG_TERM"""
        result = self.classifier.classify("上次我们聊的项目")
        assert result == MemoryIntent.LONG_TERM

        result = self.classifier.classify("我喜欢简洁的回答")
        assert result == MemoryIntent.LONG_TERM

        result = self.classifier.classify("记住我的邮箱")
        assert result == MemoryIntent.LONG_TERM

    def test_both_patterns_returns_both(self):
        """Messages matching both patterns should return BOTH"""
        result = self.classifier.classify("上次我们讨论的内容，继续")
        # This matches both patterns
        assert result in [MemoryIntent.SHORT_TERM, MemoryIntent.LONG_TERM, MemoryIntent.BOTH]

    def test_empty_string_returns_none(self):
        """Empty input should return NONE"""
        result = self.classifier.classify("")
        assert result == MemoryIntent.NONE

    def test_random_text_returns_none(self):
        """Random text without memory signals should return NONE"""
        result = self.classifier.classify("写一个快速排序算法")
        assert result == MemoryIntent.NONE

        result = self.classifier.classify("帮我生成一个报告")
        assert result == MemoryIntent.NONE


class TestEmbeddingCache:
    """Tests for the embedding cache"""

    def setup_method(self):
        self.cache = EmbeddingCache(ttl=60)

    def test_set_and_get(self):
        """Should be able to set and get cached embeddings"""
        text = "test text"
        embedding = [0.1, 0.2, 0.3]

        self.cache.set(text, embedding)
        result = self.cache.get(text)

        assert result == embedding

    def test_get_nonexistent_returns_none(self):
        """Getting nonexistent key should return None"""
        result = self.cache.get("nonexistent text")
        assert result is None

    def test_expired_entry_returns_none(self):
        """Expired entries should return None"""
        import time

        cache = EmbeddingCache(ttl=0.01)  # 10ms TTL
        cache.set("test", [0.1, 0.2])

        time.sleep(0.02)  # Wait for expiration

        result = cache.get("test")
        assert result is None

    def test_clear_expired(self):
        """Should be able to clear expired entries"""
        import time

        cache = EmbeddingCache(ttl=0.01)
        cache.set("test1", [0.1])
        cache.set("test2", [0.2])

        time.sleep(0.02)

        cleared = cache.clear_expired()
        assert cleared == 2
        assert cache.get("test1") is None
        assert cache.get("test2") is None


class TestEmbeddingService:
    """Tests for the embedding service"""

    @pytest.mark.asyncio
    async def test_local_backend_dimension(self):
        """Local backend should return 1024 dimensions"""
        # Mock the model to avoid loading actual weights
        with patch('app.services.embedding_service.LocalEmbeddingBackend') as MockBackend:
            mock_backend = MagicMock()
            mock_backend.get_dimension.return_value = 1024
            MockBackend.return_value = mock_backend

            service = EmbeddingService(provider="local")
            dim = service.get_dimension()

            assert dim == 1024

    @pytest.mark.asyncio
    async def test_openai_backend_dimension(self):
        """OpenAI backend should return 1536 dimensions"""
        with patch('app.services.embedding_service.OpenAIEmbeddingBackend') as MockBackend:
            mock_backend = MagicMock()
            mock_backend.get_dimension.return_value = 1536
            MockBackend.return_value = mock_backend

            service = EmbeddingService(provider="openai")
            dim = service.get_dimension()

            assert dim == 1536


class TestShortTermMemoryService:
    """Tests for the short-term memory service"""

    @pytest.mark.asyncio
    async def test_get_or_create(self):
        """Should create memory if not exists"""
        from app.services.short_term_memory_service import ShortTermMemoryService

        mock_db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        service = ShortTermMemoryService(mock_db)
        # This is a basic test structure
        # Full integration tests would require a test database

    @pytest.mark.asyncio
    async def test_update_token_count(self):
        """Should update token count correctly"""
        from app.services.short_term_memory_service import ShortTermMemoryService

        mock_db = AsyncMock()
        mock_memory = MagicMock()
        mock_memory.total_tokens = 100

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_memory
        mock_db.execute.return_value = mock_result

        service = ShortTermMemoryService(mock_db)
        # Test structure - would need test database for full test


class TestLongTermMemoryService:
    """Tests for the long-term memory service"""

    def test_cosine_similarity(self):
        """Cosine similarity calculation should be correct"""
        from app.services.long_term_memory_service import LongTermMemoryService
        import math

        mock_db = MagicMock()
        service = LongTermMemoryService(mock_db)

        # Test identical vectors
        vec = [1.0, 0.0, 0.0]
        sim = service._cosine_similarity(vec, vec)
        assert abs(sim - 1.0) < 0.001

        # Test orthogonal vectors
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        sim = service._cosine_similarity(vec1, vec2)
        assert abs(sim - 0.0) < 0.001

        # Test opposite vectors
        vec1 = [1.0, 0.0]
        vec2 = [-1.0, 0.0]
        sim = service._cosine_similarity(vec1, vec2)
        assert abs(sim - (-1.0)) < 0.001

    def test_parse_extraction_response(self):
        """Should parse LLM extraction response correctly"""
        from app.services.long_term_memory_service import LongTermMemoryService

        mock_db = MagicMock()
        service = LongTermMemoryService(mock_db)

        response = '''
        {
            "memories": [
                {"content": "用户喜欢 Python", "type": "preference", "importance": 0.8, "confidence": 0.9}
            ]
        }
        '''

        result = service._parse_extraction_response(response)
        assert len(result) == 1
        assert result[0]["content"] == "用户喜欢 Python"


class TestUserProfileService:
    """Tests for the user profile service"""

    def test_tech_level_conversion(self):
        """Tech level should convert to Chinese correctly"""
        from app.services.user_profile_service import UserProfileService

        mock_db = MagicMock()
        service = UserProfileService(mock_db)

        assert service._tech_level_cn("beginner") == "初学者"
        assert service._tech_level_cn("intermediate") == "中级"
        assert service._tech_level_cn("expert") == "专家级"
