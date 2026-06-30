"""
Core configuration and settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, computed_field
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # Application
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    APP_NAME: str = "LLM Chat API"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://llmchat:llmchat_secret@localhost:5432/llmchat"

    # CORS - comma-separated origins in .env
    # Example: CORS_ORIGINS=http://localhost:3000,http://localhost:5173
    CORS_ORIGINS_STR: str = "http://localhost:3000,http://localhost:5173"

    # Encryption key for API keys (32 bytes hex string)
    ENCRYPTION_KEY: str = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    # Tool defaults
    DEFAULT_TOOL_TIMEOUT: int = 30
    MAX_TOOL_ITERATIONS: int = 10

    # Proxy
    HTTP_PROXY: Optional[str] = None

    # Chat defaults
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 4096
    DEFAULT_SYSTEM_PROMPT: str = """You are a helpful assistant.

请使用 Markdown 格式回复，遵循以下规范：
- 使用标题（##、###）组织内容结构
- 使用表格展示结构化数据和对比信息
- 使用列表（- 或 1.）展示多个项目或步骤
- 使用代码块（```language）展示代码，并指定语言
- 使用粗体（**text**）强调重点内容
- 适当使用 emoji 增加可读性（如 ✅ ❌ ⚠️ 📌 等）
- 使用引用块（>）展示提示或重要说明"""

    # Memory system settings
    MEMORY_ENABLED: bool = True
    EMBEDDING_PROVIDER: str = "local"  # "local" or "openai"
    EMBEDDING_MODEL_LOCAL: str = "BAAI/bge-large-zh-v1.5"  # Local model name
    EMBEDDING_MODEL_OPENAI: str = "text-embedding-3-small"  # OpenAI model name
    EMBEDDING_DIMENSION: int = 1024  # 1024 for bge-large-zh, 1536 for OpenAI
    EMBEDDING_CACHE_ENABLED: bool = True
    EMBEDDING_CACHE_TTL: int = 3600  # Cache TTL in seconds

    # Memory injection settings
    MEMORY_TOKEN_BUDGET: int = 1000  # Max tokens for memory context
    MEMORY_CHECKPOINT_INTERVAL: int = 20  # Messages before checkpoint
    MEMORY_IDLE_TIMEOUT: int = 600  # Seconds before idle detection

    @computed_field
    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
