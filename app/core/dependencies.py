from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.team_member import TeamMember, TeamRole
from app.core.auth import current_active_user


async def get_team_admin(
    team_id,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TeamMember).where(
        TeamMember.team_id == team_id,
        TeamMember.user_id == user.id,
        TeamMember.role == TeamRole.admin,
    )
    result = await db.execute(stmt)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a team admin",
        )

    return member
