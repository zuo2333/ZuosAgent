"""
Main FastAPI application
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import async_session_maker, init_db, close_db
from app.api import (
    health_router,
    sessions_router,
    messages_router,
    chat_router,
    providers_router,
    config_router,
)
from app.api.memory import router as memory_router
from app.api.profile import router as profile_router
from app.services.config_service import ConfigService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup: Initialize database and default configuration
    async with async_session_maker() as db:
        config_service = ConfigService(db)
        await config_service.initialize_defaults()
        await db.commit()

    yield

    # Shutdown: Close database connections
    await close_db()


app = FastAPI(
    title="LLM Chat API",
    description="""
Backend API for LLM Chat Application.

## Features
- Session management with configurable providers and models
- Streaming chat with SSE (Server-Sent Events)
- Tool calling support (web search, database queries)
- Multiple provider support (OpenAI, LlamaCpp, Custom)

## Authentication
API endpoints may require authentication via API keys (configured per provider).

## API Endpoints
All API endpoints are prefixed with `/api`:
- `/api/sessions` - Session management
- `/api/sessions/{id}/messages` - Message management
- `/api/chat` - Chat endpoint (SSE streaming)
- `/api/providers` - Provider configuration
- `/api/config` - Global configuration
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Cache-Control", "Connection"],
)

# Include routers with /api prefix
app.include_router(health_router)  # Health checks at root level
app.include_router(sessions_router, prefix="/api")
app.include_router(messages_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(providers_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(profile_router, prefix="/api")


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "LLM Chat API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api",
    }
