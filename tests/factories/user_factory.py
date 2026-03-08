import uuid
from app.db.models.user import User
from app.core.security import get_password_hash


async def create_user(db_session, **kwargs):
    raw_password = kwargs.get("password", "password")
    email = kwargs.get("email", f"user_{uuid.uuid4().hex[:8]}@test.com")
    nickname = kwargs.get("nickname", f"user_{uuid.uuid4().hex[:8]}")

    user = User(
        id=uuid.uuid4(),
        email=email,
        nickname=nickname,
        hashed_password=get_password_hash(raw_password),
        is_active=True,
        is_manager=True,
        is_superuser=True,
    )

    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user
