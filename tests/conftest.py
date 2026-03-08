import pytest
import uuid
from typing import AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.db.session import get_db

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

# Создаем engine с NullPool для избежания конфликтов
engine = create_async_engine(
    TEST_DATABASE_URL, echo=True, poolclass=NullPool
)
TestingSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database session."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# Синхронная фикстура для данных пользователя
@pytest.fixture
def test_user_data() -> Dict:
    """Generate test user data (sync fixture)."""
    return {
        "email": f"user_{uuid.uuid4().hex}@test.com",
        "nickname": f"user_{uuid.uuid4().hex}",
        "password": "testpass123",
    }


@pytest.fixture
async def registered_user(client: AsyncClient, test_user_data: Dict) -> Dict:
    """Register a user and return credentials."""
    response = await client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    return test_user_data


@pytest.fixture
async def auth_token(client: AsyncClient, registered_user: Dict) -> str:
    """Get auth token for registered user."""
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
async def auth_headers(auth_token: str) -> Dict[str, str]:
    """Get auth headers."""
    return {"Authorization": f"Bearer {auth_token}"}
