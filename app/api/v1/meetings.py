import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.auth import current_active_user
from app.dependencies.services import get_meeting_service
from app.schemas.meeting import MeetingCreate, MeetingOut
from app.db.models.user import User
from app.services.meeting import MeetingService

router = APIRouter(prefix="/teams", tags=["Meetings"])


@router.post("/{team_id}/meetings", response_model=MeetingOut)
async def create_meeting(
    team_id: uuid.UUID,
    data: MeetingCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.create_meeting(session, team_id, data, current_user)


@router.get("/{team_id}/meetings", response_model=list[MeetingOut])
async def team_meetings(
    team_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.get_team_meetings(session, team_id, current_user)


@router.patch("/{team_id}/meetings/{meeting_id}/cancel")
async def cancel_team_meeting(
    team_id: uuid.UUID,
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.cancel_meeting(session, team_id, meeting_id, current_user)


@router.get("/{team_id}/meetings/{meeting_id}", response_model=MeetingOut)
async def get_team_meeting(
    team_id: uuid.UUID,
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
    service: MeetingService = Depends(get_meeting_service),
):
    return await service.get_meeting(session, team_id, meeting_id, current_user)
