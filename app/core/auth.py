import uuid
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import JWTStrategy, AuthenticationBackend

from app.db.models.user import User
from app.core.config import settings
from app.core.user_manager import UserManager
from app.db.user_db import get_user_db, get_user_db_direct
from fastapi import Depends
from fastapi_users.authentication import BearerTransport


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=3600,
    )


bearer_transport = BearerTransport(tokenUrl="/api/v1/auth/login")

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


async def get_user_manager_direct():
    async for user_db in get_user_db_direct():
        yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)
