import uuid
import secrets
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.team import Team
from app.db.models.team_member import TeamMember, TeamRole
from app.schemas.team import TeamCreate, TeamRead
from app.core.auth import current_active_user
from app.core.dependencies import get_team_admin
from sqlalchemy.future import select

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead)
async def create_team(
    data: TeamCreate,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    code = secrets.token_hex(4)

    team = Team(name=data.name, code=code)
    db.add(team)
    await db.flush()

    member = TeamMember(
        user_id=user.id,
        team_id=team.id,
        role=TeamRole.admin,
    )
    db.add(member)
    await db.commit()

    return team


@router.get("/", response_model=list[TeamRead])
async def list_teams(
    db: AsyncSession = Depends(get_db), user=Depends(current_active_user)
):
    result = await db.execute(
        select(Team).join(TeamMember).where(TeamMember.user_id == user.id)
    )
    teams = result.scalars().all()
    return teams


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    team_id: uuid.UUID,
    member=Depends(get_team_admin),
):
    return member.team
