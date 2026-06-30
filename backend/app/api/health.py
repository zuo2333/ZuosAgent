"""
Health check API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings
from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Basic health check endpoint.

    Returns the API status and version.
    Does not check database connectivity.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )


@router.get("/health/db", response_model=HealthResponse)
async def health_check_db(db: AsyncSession = Depends(get_db)):
    """
    Database connectivity health check.

    Tests the database connection and returns status.
    """
    try:
        await db.execute(text("SELECT 1"))
        return HealthResponse(
            status="healthy",
            version="0.1.0",
            database="connected"
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="0.1.0",
            database=f"disconnected: {str(e)}"
        )


@router.get("/health/ready", response_model=HealthResponse)
async def health_check_ready(db: AsyncSession = Depends(get_db)):
    """
    Readiness check for Kubernetes/container orchestration.

    Checks all dependencies:
    - Database connectivity
    - Returns 503 if not ready
    """
    try:
        await db.execute(text("SELECT 1"))
        return HealthResponse(
            status="ready",
            version="0.1.0",
            database="connected"
        )
    except Exception as e:
        # Return 503 Service Unavailable
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "version": "0.1.0",
                "database": f"disconnected: {str(e)}"
            }
        )


@router.get("/health/live", response_model=HealthResponse)
async def health_check_live():
    """
    Liveness check for Kubernetes/container orchestration.

    Returns 200 if the process is running.
    Use this for restart decisions.
    """
    return HealthResponse(
        status="alive",
        version="0.1.0"
    )
