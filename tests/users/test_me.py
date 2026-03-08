import pytest


@pytest.mark.asyncio
async def test_me(client, auth_headers, registered_user):
    """Test /me endpoint."""
    response = await client.get("/api/v1/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == registered_user["email"]
    assert data["nickname"] == registered_user["nickname"]
    assert "id" in data

@pytest.mark.asyncio
async def test_me_unauthorized(client):
    """Test /me without authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
