import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.core.meeting_permissions import ensure_team_member
from app.db.session import get_db
from app.core.auth import current_active_user
from app.db.models.meeting import Meeting
from app.db.models.meeting import MeetingParticipant
from app.schemas.meeting import MeetingCreate, MeetingOut
from app.db.models.user import User

router = APIRouter(prefix="/teams", tags=["Meetings"])


@router.post("/{team_id}/meetings", response_model=MeetingOut)
async def create_meeting(
    team_id: uuid.UUID,
    data: MeetingCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    await ensure_team_member(session, team_id, current_user.id)

    if data.start_time >= data.end_time:
        raise HTTPException(400, "Некорректное время")

    participant_ids = set(data.participant_ids)
    participant_ids.add(current_user.id)

    # Проверяем, что все участники состоят в команде
    for user_id in participant_ids:
        await ensure_team_member(session, team_id, user_id)

    # Проверка пересечений В РАМКАХ КОМАНДЫ
    stmt = (
        select(Meeting)
        .join(MeetingParticipant)
        .where(
            Meeting.team_id == team_id,
            MeetingParticipant.user_id.in_(participant_ids),
            Meeting.is_cancelled.is_(False),
            Meeting.start_time < data.end_time,
            Meeting.end_time > data.start_time,
        )
    )

    if await session.scalar(stmt):
        raise HTTPException(
            status_code=400,
            detail="Пересечение встреч в команде",
        )

    meeting = Meeting(
        title=data.title,
        start_time=data.start_time,
        end_time=data.end_time,
        team_id=team_id,
        creator_id=current_user.id,
    )
    session.add(meeting)
    await session.flush()

    for user_id in participant_ids:
        session.add(
            MeetingParticipant(
                meeting_id=meeting.id,
                user_id=user_id,
            )
        )

    await session.commit()

    stmt = (
        select(Meeting)
        .options(
            selectinload(Meeting.participants)
            .selectinload(MeetingParticipant.user)
        )
        .where(Meeting.id == meeting.id)
    )

    meeting = await session.scalar(stmt)

    return meeting


@router.get("/{team_id}/meetings", response_model=list[MeetingOut])
async def team_meetings(
    team_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    await ensure_team_member(session, team_id, current_user.id)

    stmt = (
        select(Meeting)
        .options(
            selectinload(Meeting.participants).selectinload(MeetingParticipant.user)
        )
        .join(MeetingParticipant)
        .where(
            Meeting.team_id == team_id,
            MeetingParticipant.user_id == current_user.id,
            Meeting.is_cancelled.is_(False),
        )
        .order_by(Meeting.start_time)
    )

    result = await session.scalars(stmt)
    return result.all()


@router.patch("/{team_id}/meetings/{meeting_id}/cancel")
async def cancel_team_meeting(
    team_id: uuid.UUID,
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    meeting = await session.get(Meeting, meeting_id)

    if not meeting or meeting.team_id != team_id:
        raise HTTPException(404, "Встреча не найдена")

    if meeting.creator_id != current_user.id:
        raise HTTPException(403, "Недостаточно прав")

    meeting.is_cancelled = True
    await session.commit()
    return {"status": "cancelled"}


@router.get(
    "/{team_id}/meetings/{meeting_id}",
    response_model=MeetingOut,
)
async def get_team_meeting(
    team_id: uuid.UUID,
    meeting_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    # 1. Проверка, что пользователь в команде
    await ensure_team_member(session, team_id, current_user.id)

    # 2. Получаем встречу
    stmt = (
        select(Meeting)
        .options(
            selectinload(Meeting.participants).selectinload(MeetingParticipant.user)
        )
        .join(MeetingParticipant)
        .where(
            Meeting.id == meeting_id,
            Meeting.team_id == team_id,
            MeetingParticipant.user_id == current_user.id,
        )
    )
    meeting = await session.scalar(stmt)

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Встреча не найдена или нет доступа",
        )

    return meeting
