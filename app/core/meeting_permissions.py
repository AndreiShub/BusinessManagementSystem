from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.team_member import TeamMember


async def ensure_team_member(
    session: AsyncSession,
    team_id: int,
    user_id: UUID,
):
    stmt = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user_id,
    )
    if not await session.scalar(stmt):
        raise HTTPException(
            status_code=403,
            detail="Вы не участник команды",
        )
