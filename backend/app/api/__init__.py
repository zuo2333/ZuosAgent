"""
API routes module
"""
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.messages import router as messages_router
from app.api.chat import router as chat_router
from app.api.providers import router as providers_router
from app.api.config import router as config_router

__all__ = [
    "health_router",
    "sessions_router",
    "messages_router",
    "chat_router",
    "providers_router",
    "config_router",
]
