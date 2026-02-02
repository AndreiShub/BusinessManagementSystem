from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.team_member import TeamMember, TeamRole


async def ensure_can_manage_tasks(
    db: AsyncSession,
    user_id,
    team_id,
):
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id,
            TeamMember.role.in_([TeamRole.admin, TeamRole.manager]),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to manage tasks",
        )
