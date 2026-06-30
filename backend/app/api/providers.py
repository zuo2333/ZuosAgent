"""
Provider configuration API routes.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services import ProviderService
from app.schemas.api import (
    ProviderCreate,
    ProviderUpdate,
    ProviderResponse,
    ProviderListResponse,
)

router = APIRouter(prefix="/providers", tags=["providers"])


def get_provider_service(db: AsyncSession = Depends(get_db)) -> ProviderService:
    """Dependency for provider service."""
    return ProviderService(db)


@router.post("", response_model=ProviderResponse, status_code=201)
async def create_provider(
    data: ProviderCreate,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Create a new provider configuration.

    API keys are encrypted before storage.
    """
    # Check if provider ID already exists
    existing = await service.get(data.id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Provider with ID '{data.id}' already exists"
        )

    provider = await service.create(data)
    return service.to_response(provider)


@router.get("", response_model=ProviderListResponse)
async def list_providers(
    skip: int = Query(default=0, ge=0, description="Number of providers to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum providers to return"),
    provider_type: Optional[str] = Query(default=None, description="Filter by provider type"),
    is_active: Optional[bool] = Query(default=None, description="Filter by active status"),
    service: ProviderService = Depends(get_provider_service)
):
    """
    Get list of providers.

    Returns paginated list of providers (without API keys).
    """
    providers, total = await service.get_list(
        skip=skip,
        limit=limit,
        provider_type=provider_type,
        is_active=is_active
    )
    return ProviderListResponse(
        providers=[service.to_response(p) for p in providers],
        total=total
    )


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Get a specific provider by ID.

    Returns provider details without the API key.
    """
    provider = await service.get(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return service.to_response(provider)


@router.put("/{provider_id}", response_model=ProviderResponse)
@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: str,
    data: ProviderUpdate,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Update a provider configuration.

    Only provided fields will be updated.
    API keys are encrypted before storage.
    """
    provider = await service.update(provider_id, data)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return service.to_response(provider)


@router.delete("/{provider_id}", status_code=204)
async def delete_provider(
    provider_id: str,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Delete a provider configuration.

    Note: Sessions using this provider will fall back to default.
    """
    deleted = await service.delete(provider_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Provider not found")
    return None


@router.post("/{provider_id}/test")
async def test_provider(
    provider_id: str,
    service: ProviderService = Depends(get_provider_service)
):
    """
    Test provider connection.

    Validates that the provider is reachable and properly configured.
    """
    from app.providers.factory import create_provider
    from app.providers.base import ProviderConfig, ProviderError

    provider_model = await service.get(provider_id)
    if not provider_model:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Get decrypted API key
    api_key = await service.get_decrypted_api_key(provider_id)

    # Build provider config
    provider_config = ProviderConfig.from_db_model(provider_model, api_key)

    # Create provider instance and validate connection
    try:
        provider = create_provider(provider_config)
        is_valid = await provider.validate_connection()

        if is_valid:
            return {"success": True, "message": "Connection successful"}
        else:
            return {"success": False, "message": "Connection failed - provider unreachable"}

    except ProviderError as e:
        return {"success": False, "message": str(e)}
    except Exception as e:
        return {"success": False, "message": f"Connection test failed: {str(e)}"}
