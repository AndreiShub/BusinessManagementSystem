import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi import Depends

from app.db.models.user import User
from app.core.config import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.secret_key
    verification_token_secret = settings.secret_key

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} has registered.")
