import pytest
import uuid
from typing import AsyncGenerator, Dict
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.core.auth import get_jwt_strategy
from app.db.models.team_member import TeamMember
from app.db.models.user import User
from app.main import app
from app.core.config import settings
from app.db.session import get_db
from tests.factories.user_factory import create_user
from tests.factories.team_factory import create_team

from app.core.auth import auth_backend

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

# Создаем engine с NullPool для избежания конфликтов
engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)
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
async def user(db_session: AsyncSession):
    return await create_user(db_session)

@pytest.fixture
async def team(db_session: AsyncSession, user):
    team = await create_team(db_session, creator=user)
    # добавляем пользователя в команду
    db_session.add(TeamMember(team_id=team.id, user_id=user.id))
    await db_session.commit()
    return team

@pytest.fixture
async def auth_headers(db_session):
    user = await create_user(db_session)

    strategy = auth_backend.get_strategy()

    token = await strategy.write_token(user)

    return {
        "Authorization": f"Bearer {token}"
    }