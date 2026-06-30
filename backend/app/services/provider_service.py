"""
Provider service for managing model providers.
"""
import uuid
import re
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Provider
from app.schemas.api import ProviderCreate, ProviderUpdate
from app.utils.encryption import encrypt_api_key, decrypt_api_key


def generate_slug_id(name: str) -> str:
    """Generate a URL-safe slug ID from a name."""
    # Convert to lowercase and replace non-alphanumeric with hyphens
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    # Limit length and add random suffix to avoid collisions
    slug = slug[:40] if len(slug) > 40 else slug
    suffix = uuid.uuid4().hex[:8]
    return f"{slug}-{suffix}" if slug else suffix


class ProviderService:
    """Service for managing model providers."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the provider service.

        Args:
            db: AsyncSession for database operations.
        """
        self.db = db

    async def create(self, data: ProviderCreate) -> Provider:
        """
        Create a new provider.

        Args:
            data: Provider creation data.

        Returns:
            Created Provider object.
        """
        # Encrypt API key if provided
        encrypted_key = None
        if data.api_key:
            encrypted_key = encrypt_api_key(data.api_key)

        # Auto-generate ID if not provided
        provider_id = data.id or generate_slug_id(data.name)

        provider = Provider(
            id=provider_id,
            name=data.name,
            provider_type=data.provider_type,
            endpoint=data.base_url,  # Map base_url to endpoint
            api_key=encrypted_key,
            config=data.config,
            is_active=data.is_active,
        )
        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)
        return provider

    async def get(self, provider_id: str) -> Optional[Provider]:
        """
        Get a provider by ID.

        Args:
            provider_id: Provider ID.

        Returns:
            Provider object or None.
        """
        result = await self.db.execute(
            select(Provider).where(Provider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def get_list(
        self,
        skip: int = 0,
        limit: int = 20,
        provider_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Provider], int]:
        """
        Get list of providers with pagination.

        Args:
            skip: Number of providers to skip.
            limit: Maximum number of providers to return.
            provider_type: Filter by provider type.
            is_active: Filter by active status.

        Returns:
            Tuple of (providers list, total count).
        """
        query = select(Provider)

        if provider_type:
            query = query.where(Provider.provider_type == provider_type)
        if is_active is not None:
            query = query.where(Provider.is_active == is_active)

        # Get total count
        count_query = select(func.count(Provider.id))
        if provider_type:
            count_query = count_query.where(Provider.provider_type == provider_type)
        if is_active is not None:
            count_query = count_query.where(Provider.is_active == is_active)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        query = query.order_by(Provider.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        providers = list(result.scalars().all())

        return providers, total

    async def update(self, provider_id: str, data: ProviderUpdate) -> Optional[Provider]:
        """
        Update a provider.

        Args:
            provider_id: Provider ID.
            data: Provider update data.

        Returns:
            Updated Provider object or None.
        """
        provider = await self.get(provider_id)
        if not provider:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "api_key" and value is not None:
                # Encrypt the new API key
                value = encrypt_api_key(value)
            elif key == "base_url":
                # Map base_url to endpoint
                key = "endpoint"
            setattr(provider, key, value)

        await self.db.flush()
        await self.db.refresh(provider)
        return provider

    async def delete(self, provider_id: str) -> bool:
        """
        Delete a provider.

        Args:
            provider_id: Provider ID.

        Returns:
            True if deleted, False if not found.
        """
        provider = await self.get(provider_id)
        if not provider:
            return False

        await self.db.delete(provider)
        await self.db.flush()
        return True

    async def get_decrypted_api_key(self, provider_id: str) -> Optional[str]:
        """
        Get the decrypted API key for a provider.

        Args:
            provider_id: Provider ID.

        Returns:
            Decrypted API key or None.
        """
        provider = await self.get(provider_id)
        if not provider or not provider.api_key:
            return None

        try:
            return decrypt_api_key(provider.api_key)
        except Exception:
            return None

    def to_response(self, provider: Provider) -> dict:
        """
        Convert a Provider model to response dict (without API key).

        Args:
            provider: Provider model.

        Returns:
            Dictionary for response.
        """
        return {
            "id": provider.id,
            "name": provider.name,
            "provider_type": provider.provider_type,
            "base_url": provider.endpoint,  # Map endpoint to base_url
            "config": provider.config,
            "is_active": provider.is_active,
        }
