from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from tests.factories.user_factory import create_user


@pytest.mark.asyncio
async def test_me(client, auth_headers, auth_user):

    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == auth_user.email


@pytest.mark.asyncio
async def test_me_unauthorized(client):
    """Test /me without authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
