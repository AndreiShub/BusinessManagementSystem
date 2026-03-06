import uuid
from app.db.models.user import User
from app.core.security import get_password_hash
MAX_BCRYPT_BYTES = 72

async def create_user(db_session, **kwargs):
    raw_password = kwargs.get("password", "password")
    truncated_password = raw_password.encode("utf-8")[:MAX_BCRYPT_BYTES].decode("utf-8", errors="ignore")

    user = User(
        id=uuid.uuid4(),
        email=kwargs.get("email", "user@test.com"),
        nickname=kwargs.get("nickname", "tester"),
        hashed_password=get_password_hash(truncated_password)[:72],
        is_active=True,
        is_verified=True,
        is_superuser=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user