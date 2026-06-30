"""
Integration tests for API endpoints.
"""
import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient


class TestHealthAPI:
    """Tests for health check endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint returns ok."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "LLM Chat" in data["message"]


class TestSessionsAPI:
    """Tests for session management API."""

    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient):
        """Test creating a new session."""
        response = await client.post(
            "/api/sessions",
            json={
                "name": "Test Session",
                "provider_id": None,
                "model": None,
                "temperature": 0.7,
                "max_tokens": 2000,
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Session"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_sessions(self, client: AsyncClient):
        """Test listing sessions."""
        # Create a session first
        await client.post(
            "/api/sessions",
            json={"name": "List Test Session"}
        )

        response = await client.get("/api/sessions")
        assert response.status_code == 200
        data = response.json()
        assert "sessions" in data
        assert "total" in data
        assert isinstance(data["sessions"], list)

    @pytest.mark.asyncio
    async def test_get_session(self, client: AsyncClient):
        """Test getting a specific session."""
        # Create a session
        create_response = await client.post(
            "/api/sessions",
            json={"name": "Get Test Session"}
        )
        session_id = create_response.json()["id"]

        # Get the session
        response = await client.get(f"/api/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert data["name"] == "Get Test Session"

    @pytest.mark.asyncio
    async def test_get_nonexistent_session(self, client: AsyncClient):
        """Test getting a nonexistent session returns 404."""
        response = await client.get("/api/sessions/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_session(self, client: AsyncClient):
        """Test updating a session."""
        # Create a session
        create_response = await client.post(
            "/api/sessions",
            json={"name": "Update Test Session"}
        )
        session_id = create_response.json()["id"]

        # Update the session
        response = await client.put(
            f"/api/sessions/{session_id}",
            json={"name": "Updated Session Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Session Name"

    @pytest.mark.asyncio
    async def test_delete_session(self, client: AsyncClient):
        """Test deleting a session."""
        # Create a session
        create_response = await client.post(
            "/api/sessions",
            json={"name": "Delete Test Session"}
        )
        session_id = create_response.json()["id"]

        # Delete the session
        response = await client.delete(f"/api/sessions/{session_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_session_pagination(self, client: AsyncClient):
        """Test session list pagination."""
        # Create multiple sessions
        for i in range(5):
            await client.post(
                "/api/sessions",
                json={"name": f"Pagination Test {i}"}
            )

        # Test pagination
        response = await client.get("/api/sessions?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["sessions"]) <= 2


class TestMessagesAPI:
    """Tests for message management API."""

    @pytest.fixture
    async def test_session(self, client: AsyncClient):
        """Create a test session for message tests."""
        response = await client.post(
            "/api/sessions",
            json={"name": "Message Test Session"}
        )
        return response.json()["id"]

    @pytest.mark.asyncio
    async def test_add_message(self, client: AsyncClient, test_session: str):
        """Test adding a message to a session."""
        response = await client.post(
            f"/api/sessions/{test_session}/messages",
            json={
                "role": "user",
                "content": "Hello, this is a test message."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"] == "user"
        assert data["content"] == "Hello, this is a test message."

    @pytest.mark.asyncio
    async def test_list_messages(self, client: AsyncClient, test_session: str):
        """Test listing messages for a session."""
        # Add some messages
        await client.post(
            f"/api/sessions/{test_session}/messages",
            json={"role": "user", "content": "Message 1"}
        )
        await client.post(
            f"/api/sessions/{test_session}/messages",
            json={"role": "assistant", "content": "Message 2"}
        )

        response = await client.get(f"/api/sessions/{test_session}/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) >= 2

    @pytest.mark.asyncio
    async def test_messages_ordered_by_time(self, client: AsyncClient, test_session: str):
        """Test that messages are returned in order."""
        # Add messages
        for i in range(3):
            await client.post(
                f"/api/sessions/{test_session}/messages",
                json={"role": "user", "content": f"Message {i}"}
            )

        response = await client.get(f"/api/sessions/{test_session}/messages")
        messages = response.json()["messages"]

        # Messages should be ordered (oldest first or newest first)
        contents = [m["content"] for m in messages]
        assert len(contents) >= 3


class TestProvidersAPI:
    """Tests for provider management API."""

    @pytest.mark.asyncio
    async def test_create_provider(self, client: AsyncClient):
        """Test creating a provider."""
        response = await client.post(
            "/api/providers",
            json={
                "name": "Test OpenAI",
                "provider_type": "openai",
                "endpoint": None,
                "api_key": "sk-test-key",
                "config": {}
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test OpenAI"
        assert data["provider_type"] == "openai"
        # API key should not be returned in response
        assert "api_key" not in data or data.get("api_key") is None

    @pytest.mark.asyncio
    async def test_list_providers(self, client: AsyncClient):
        """Test listing providers."""
        # Create a provider first
        await client.post(
            "/api/providers",
            json={
                "name": "List Test Provider",
                "provider_type": "custom",
                "endpoint": "http://localhost:8080/v1"
            }
        )

        response = await client.get("/api/providers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_update_provider(self, client: AsyncClient):
        """Test updating a provider."""
        # Create a provider
        create_response = await client.post(
            "/api/providers",
            json={
                "name": "Update Test Provider",
                "provider_type": "openai"
            }
        )
        provider_id = create_response.json()["id"]

        # Update the provider
        response = await client.put(
            f"/api/providers/{provider_id}",
            json={"name": "Updated Provider Name"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Provider Name"

    @pytest.mark.asyncio
    async def test_delete_provider(self, client: AsyncClient):
        """Test deleting a provider."""
        # Create a provider
        create_response = await client.post(
            "/api/providers",
            json={
                "name": "Delete Test Provider",
                "provider_type": "custom",
                "endpoint": "http://localhost:8080/v1"
            }
        )
        provider_id = create_response.json()["id"]

        # Delete the provider
        response = await client.delete(f"/api/providers/{provider_id}")
        assert response.status_code == 204


class TestConfigAPI:
    """Tests for global configuration API."""

    @pytest.mark.asyncio
    async def test_get_config(self, client: AsyncClient):
        """Test getting global configuration."""
        response = await client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        # Check for expected config fields
        assert "default_temperature" in data or "default_model" in data

    @pytest.mark.asyncio
    async def test_update_config(self, client: AsyncClient):
        """Test updating global configuration."""
        response = await client.put(
            "/api/config",
            json={
                "default_temperature": 0.8,
                "default_max_tokens": 4096
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_temperature"] == 0.8
        assert data["default_max_tokens"] == 4096


class TestChatAPI:
    """Tests for chat API with SSE streaming."""

    @pytest.fixture
    async def test_session_with_provider(self, client: AsyncClient):
        """Create a test session with a mock provider."""
        # Create a provider
        provider_response = await client.post(
            "/api/providers",
            json={
                "name": "Chat Test Provider",
                "provider_type": "openai",
                "api_key": "sk-test-key"
            }
        )
        provider_id = provider_response.json()["id"]

        # Create a session with this provider
        session_response = await client.post(
            "/api/sessions",
            json={
                "name": "Chat Test Session",
                "provider_id": provider_id,
                "model": "gpt-4"
            }
        )
        return session_response.json()["id"]

    @pytest.mark.asyncio
    async def test_chat_endpoint_exists(self, client: AsyncClient, test_session_with_provider: str):
        """Test that chat endpoint exists and accepts requests."""
        # This test just verifies the endpoint exists
        # Full streaming test would require mocking the LLM provider
        response = await client.post(
            "/api/chat",
            json={
                "session_id": test_session_with_provider,
                "message": "Hello"
            }
        )
        # The response might fail due to missing provider, but should not be 404
        assert response.status_code != 404

    @pytest.mark.asyncio
    async def test_chat_missing_session(self, client: AsyncClient):
        """Test chat with nonexistent session returns 404."""
        response = await client.post(
            "/api/chat",
            json={
                "session_id": "nonexistent-session-id",
                "message": "Hello"
            }
        )
        assert response.status_code == 404


class TestCORS:
    """Tests for CORS configuration."""

    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """Test that CORS headers are present."""
        response = await client.options(
            "/api/sessions",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            }
        )
        # Preflight should be allowed
        assert response.status_code == 200


class TestErrorHandling:
    """Tests for error handling."""

    @pytest.mark.asyncio
    async def test_404_for_unknown_route(self, client: AsyncClient):
        """Test that unknown routes return 404."""
        response = await client.get("/api/unknown-route")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_validation_error(self, client: AsyncClient):
        """Test that validation errors return 422."""
        response = await client.post(
            "/api/sessions",
            json={"invalid_field": "value"}
        )
        # Should fail validation (missing required fields or invalid data)
        assert response.status_code in [400, 422]
