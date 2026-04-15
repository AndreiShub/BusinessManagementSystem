import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.services import get_team_service
from app.schemas.team import TeamCreate, TeamRead
from app.core.auth import current_active_user
from app.services.team import TeamService

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamRead)
async def create_team(
    data: TeamCreate,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
    service: TeamService = Depends(get_team_service),
):
    return await service.create_team(db, data, user)


@router.get("/", response_model=list[TeamRead])
async def list_teams(
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TeamService = Depends(get_team_service),
):
    return await service.list_teams(db, user)


@router.get("/{team_id}", response_model=TeamRead)
async def get_team(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TeamService = Depends(get_team_service),
):
    return await service.get_team(db, team_id, user)
