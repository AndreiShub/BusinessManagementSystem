import pytest
from tests.factories.user_factory import create_user


@pytest.mark.asyncio
async def test_logout(client, db_session):
    # 1. создаем пользователя через factory
    user = await create_user(
        db_session,
        password="password",
    )

    # 2. логинимся
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user.email,
            "password": "password",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # 3. делаем logout
    response = await client.post(
        "/api/v1/auth/logout",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    # 4. проверяем ответ
    assert response.status_code == 204