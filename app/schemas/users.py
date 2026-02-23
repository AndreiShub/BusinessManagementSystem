from typing import Optional
import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    nickname: str | None = None
    is_manager: bool


class UserCreate(schemas.BaseUserCreate):
    nickname: str | None = None
    is_manager: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[str]
    nickname: Optional[str]