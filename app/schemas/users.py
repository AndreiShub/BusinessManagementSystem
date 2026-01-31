import uuid
from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    is_manager: bool


class UserCreate(schemas.BaseUserCreate):
    is_manager: bool = False


class UserUpdate(schemas.BaseUserUpdate):
    is_manager: bool
