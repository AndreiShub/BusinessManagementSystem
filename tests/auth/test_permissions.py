import pytest

@pytest.mark.asyncio
async def test_me_unauthorized(client):
    """Test /me without authentication."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data