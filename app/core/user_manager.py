import uuid
from fastapi_users import BaseUserManager, UUIDIDMixin

from app.db.models.user import User
from app.core.config import settings
from app.schemas.users import UserCreate
from app.services.nickname import NicknameService


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def create(self, user_create, safe=False, request=None) -> User:
        user_dict = user_create.create_update_dict()
        nickname_service = NicknameService(self.user_db)

        if user_dict.get("nickname"):
            if await self.user_db.is_nickname_taken(user_dict["nickname"]):
                user_dict["nickname"] = await nickname_service.generate_nickname_unique(
                    user_dict["email"]
                )
        else:
            user_dict["nickname"] = await nickname_service.generate_nickname_unique(
                user_dict["email"]
            )

        updated_user_create = UserCreate(**user_dict)
        return await super().create(updated_user_create, safe, request)

    async def on_after_register(self, user: User, request=None):
        print(f"User {user.email} has registered.")
