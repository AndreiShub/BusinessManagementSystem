import pytest


@pytest.mark.asyncio
async def test_register(client, test_user_data):
    """Test registration endpoint."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user_data["email"]
    assert data["nickname"] == test_user_data["nickname"]
    assert "id" in data
    assert "hashed_password" not in data
