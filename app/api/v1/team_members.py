from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import current_active_user
from app.dependencies.services import get_team_member_service
from app.schemas.team import JoinTeamRequest
from app.services.team_member import TeamMemberService

router = APIRouter(prefix="/teams", tags=["team-members"])


@router.post("/join")
async def join_team(
    data: JoinTeamRequest,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TeamMemberService = Depends(get_team_member_service),
):
    return await service.join_team(db, data.code, user)


@router.get("/{team_id}/members")
async def get_team_members(
    team_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TeamMemberService = Depends(get_team_member_service),
):
    return await service.get_team_members(db, team_id)
