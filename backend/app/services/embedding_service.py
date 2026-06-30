"""
Embedding service for vector generation
Supports local (sentence-transformers) and OpenAI embedding models
"""
import hashlib
import time
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from functools import lru_cache

from app.core.config import settings


class EmbeddingBackend(ABC):
    """Abstract base class for embedding backends"""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the dimension of embeddings"""
        pass


class LocalEmbeddingBackend(EmbeddingBackend):
    """Local embedding backend using sentence-transformers"""

    def __init__(self, model_name: str = "BAAI/bge-large-zh-v1.5"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Install with: pip install sentence-transformers"
                )
        return self._model

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        model = self._get_model()
        embeddings = model.encode(texts, normalize_embeddings=True)
        return [e.tolist() for e in embeddings]

    def get_dimension(self) -> int:
        """Return the dimension of embeddings"""
        # bge-large-zh-v1.5: 1024 dimensions
        return 1024


class OpenAIEmbeddingBackend(EmbeddingBackend):
    """OpenAI embedding backend"""

    def __init__(
        self,
        model_name: str = "text-embedding-3-small",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        """Lazy load the OpenAI client"""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                kwargs = {}
                if self.api_key:
                    kwargs["api_key"] = self.api_key
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self._client = AsyncOpenAI(**kwargs)
            except ImportError:
                raise ImportError(
                    "openai not installed. "
                    "Install with: pip install openai"
                )
        return self._client

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        client = self._get_client()
        response = await client.embeddings.create(
            model=self.model_name,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        client = self._get_client()
        response = await client.embeddings.create(
            model=self.model_name,
            input=texts
        )
        return [d.embedding for d in response.data]

    def get_dimension(self) -> int:
        """Return the dimension of embeddings"""
        # text-embedding-3-small: 1536 dimensions
        return 1536


class EmbeddingCache:
    """Simple in-memory cache for embeddings"""

    def __init__(self, ttl: int = 3600):
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}  # {hash: (embedding, timestamp)}

    def _hash(self, text: str) -> str:
        """Generate hash key for text"""
        return hashlib.sha256(text.encode()).hexdigest()

    def get(self, text: str) -> Optional[List[float]]:
        """Get cached embedding if exists and not expired"""
        key = self._hash(text)
        if key in self._cache:
            embedding, timestamp = self._cache[key]
            if time.time() - timestamp < self.ttl:
                return embedding
            del self._cache[key]
        return None

    def set(self, text: str, embedding: List[float]) -> None:
        """Cache an embedding"""
        key = self._hash(text)
        self._cache[key] = (embedding, time.time())

    def clear_expired(self) -> int:
        """Clear expired entries, return count of cleared"""
        now = time.time()
        expired_keys = [
            k for k, (_, ts) in self._cache.items()
            if now - ts >= self.ttl
        ]
        for k in expired_keys:
            del self._cache[k]
        return len(expired_keys)


class EmbeddingService:
    """
    Main embedding service with configurable backend and optional caching
    """

    def __init__(
        self,
        provider: str = "local",
        model_name: Optional[str] = None,
        cache_enabled: bool = True,
        cache_ttl: int = 3600,
        openai_api_key: Optional[str] = None,
        openai_base_url: Optional[str] = None
    ):
        self.provider = provider
        self.cache_enabled = cache_enabled
        self._cache = EmbeddingCache(ttl=cache_ttl) if cache_enabled else None

        if provider == "local":
            model = model_name or settings.EMBEDDING_MODEL_LOCAL
            self._backend = LocalEmbeddingBackend(model_name=model)
        elif provider == "openai":
            model = model_name or settings.EMBEDDING_MODEL_OPENAI
            self._backend = OpenAIEmbeddingBackend(
                model_name=model,
                api_key=openai_api_key,
                base_url=openai_base_url
            )
        else:
            raise ValueError(f"Unknown embedding provider: {provider}")

    async def embed(self, text: str) -> List[float]:
        """Generate embedding for a single text (with caching)"""
        # Check cache
        if self._cache:
            cached = self._cache.get(text)
            if cached is not None:
                return cached

        # Generate embedding
        embedding = await self._backend.embed(text)

        # Cache result
        if self._cache:
            self._cache.set(text, embedding)

        return embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (with caching)"""
        results = []
        uncached_texts = []
        uncached_indices = []

        # Check cache for each text
        if self._cache:
            for i, text in enumerate(texts):
                cached = self._cache.get(text)
                if cached is not None:
                    results.append((i, cached))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))

        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = await self._backend.embed_batch(uncached_texts)

            # Cache new embeddings
            if self._cache:
                for text, embedding in zip(uncached_texts, new_embeddings):
                    self._cache.set(text, embedding)

            # Add to results
            for idx, embedding in zip(uncached_indices, new_embeddings):
                results.append((idx, embedding))

        # Sort by original index and return
        results.sort(key=lambda x: x[0])
        return [e for _, e in results]

    def get_dimension(self) -> int:
        """Return the dimension of embeddings"""
        return self._backend.get_dimension()

    def clear_cache(self) -> None:
        """Clear the embedding cache"""
        if self._cache:
            self._cache._cache.clear()


# Singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService(
            provider=settings.EMBEDDING_PROVIDER,
            cache_enabled=settings.EMBEDDING_CACHE_ENABLED,
            cache_ttl=settings.EMBEDDING_CACHE_TTL
        )
    return _embedding_service


def reset_embedding_service() -> None:
    """Reset the embedding service singleton (for testing)"""
    global _embedding_service
    _embedding_service = None
