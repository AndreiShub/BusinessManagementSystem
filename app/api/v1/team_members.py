from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.team import Team
from app.db.models.team_member import TeamMember, TeamRole
from app.core.auth import current_active_user
from app.schemas.team import JoinTeamRequest
from app.core.dependencies import get_team_admin
from app.schemas.team import TeamMemberRead

router = APIRouter(prefix="/teams", tags=["team-members"])


@router.post("/join")
async def join_team(
    data: JoinTeamRequest,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Ищем команду по коду
    result = await db.execute(
        select(Team).where(Team.code == data.code)
    )
    team = result.scalar_one_or_none()

    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found",
        )

    # 2. Проверяем, что пользователь не состоит в команде
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team.id,
            TeamMember.user_id == user.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a member of this team",
        )

    # 3. Добавляем пользователя
    member = TeamMember(
        user_id=user.id,
        team_id=team.id,
        role=TeamRole.user,
    )
    db.add(member)
    await db.commit()

    return {"message": "Joined the team successfully"}

@router.get("/{team_id}/members", response_model=list[TeamMemberRead])
async def list_team_members(
    team_id,
    member=Depends(get_team_admin),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TeamMember).where(TeamMember.team_id == team_id)
    )
    return result.scalars().all()