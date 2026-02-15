from typing import Optional
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.models.user import User
from app.db.session import get_db


class CustomSQLAlchemyUserDatabase(SQLAlchemyUserDatabase):
    async def get_by_nickname(self, nickname: str) -> Optional[User]:
        statement = select(self.user_table).where(self.user_table.nickname == nickname)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def is_nickname_taken(self, nickname: str) -> bool:
        user = await self.get_by_nickname(nickname)
        return user is not None


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield CustomSQLAlchemyUserDatabase(session, User)


async def get_user_db_direct():
    async for db in get_db():
        yield CustomSQLAlchemyUserDatabase(db, User)
