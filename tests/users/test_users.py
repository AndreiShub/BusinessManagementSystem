import pytest

from tests.factories.user_factory import create_user


@pytest.mark.asyncio
async def test_get_user(client, db_session):
    user = await create_user(
        db_session,
        password="password",
    )

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password"},
    )

    token = login.json()["access_token"]

    response = await client.get(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == user.email


@pytest.mark.asyncio
async def test_update_user(client, db_session):
    user = await create_user(
        db_session,
        password="password",
    )

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password"},
    )

    token = login.json()["access_token"]

    response = await client.patch(
        f"/api/v1/users/{user.id}",
        json={"nickname": "newnickname"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "newnickname"


@pytest.mark.asyncio
async def test_delete_user(client, db_session):
    user = await create_user(
        db_session,
        password="password",
    )

    login = await client.post(
        "/api/v1/auth/login",
        data={"username": user.email, "password": "password"},
    )

    token = login.json()["access_token"]

    response = await client.delete(
        f"/api/v1/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_user_unauthorized(client, db_session):
    user = await create_user(db_session)

    response = await client.get(f"/api/v1/users/{user.id}")

    assert response.status_code == 401
