from datetime import datetime, timezone
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from app.core.auth import fastapi_users, auth_backend
from app.db.models.meeting import Meeting, MeetingParticipant
from app.db.models.task import Task, TaskAssignee
from app.db.models.user import User
from app.db.session import get_db
from app.db.user_db import get_user_db
from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.api.v1.teams import router as teams_router
from app.api.v1.team_members import router as team_members_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.meetings import router as meetings_router
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.auth import current_active_user
from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1")

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

router.include_router(teams_router)

router.include_router(team_members_router)

router.include_router(tasks_router)

router.include_router(meetings_router)


@router.patch("/users/me")
async def update_me(
    user_update: UserUpdate,
    user=Depends(fastapi_users.current_user()),
    user_db=Depends(get_user_db),
):
    # обновляем только те поля, что пришли
    updated = False
    if user_update.email is not None:
        user.email = user_update.email
        updated = True
    if user_update.nickname is not None:
        user.nickname = user_update.nickname
        updated = True

    if updated:
        await user_db.update(user)

    return {
        "email": user.email,
        "nickname": user.nickname,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "is_manager": user.is_manager,
    }


@router.get("/events")
async def get_events(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    # --- год и месяц ---
    today = datetime.now(timezone.utc)
    year = year or today.year
    month = month or today.month

    # корректные даты с таймзоной UTC
    start_date = datetime(year, month, 1, tzinfo=timezone.utc)
    if month == 12:
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end_date = datetime(year, month + 1, 1, tzinfo=timezone.utc)

    events: list[dict] = []

    # ---------- TASKS ----------
    task_query = (
        select(Task)
        .join(TaskAssignee, Task.id == TaskAssignee.task_id)
        .where(
            TaskAssignee.user_id == current_user.id,
            Task.deadline >= start_date,
            Task.deadline < end_date,
        )
)
    tasks = (await db.execute(task_query)).scalars().all()

    for task in tasks:
        # собираем всех исполнителей для задачи
        assignees_query = select(TaskAssignee.user_id).where(TaskAssignee.task_id == task.id)
        assignee_rows = (await db.execute(assignees_query)).scalars().all()

        events.append({
            "id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "event_type": "task",
            "date": task.deadline.date().isoformat(),
            "time": task.deadline.strftime("%H:%M") if task.deadline.time() else None,
            "status": task.status.value if task.status else None,
            "team_id": str(task.team_id),
            "assignee_ids": [str(uid) for uid in assignee_rows],
        })

    # ---------- MEETINGS ----------
    meeting_query = (
        select(Meeting)
        .join(MeetingParticipant)
        .where(
            MeetingParticipant.user_id == current_user.id,
            Meeting.start_time >= start_date,
            Meeting.start_time < end_date,
        )
    )
    meetings = (await db.execute(meeting_query)).scalars().all()

    now = datetime.now(timezone.utc)
    for meeting in meetings:
        if meeting.is_cancelled:
            status = "cancelled"
        elif meeting.start_time <= now <= meeting.end_time:
            status = "in_progress"
        else:
            status = "planned"

        participants = [str(p.user_id) for p in meeting.participants]

        events.append({
            "id": f"meeting:{meeting.id}",
            "title": meeting.title,
            "description": "Встреча",
            "event_type": "meeting",
            "date": meeting.start_time.date().isoformat(),
            "time": meeting.start_time.strftime("%H:%M"),
            "status": status,
            "team_id": str(meeting.team_id),
            "participants": participants,
        })

    # сортировка по дате и времени
    events.sort(key=lambda e: (e["date"], e["time"] or ""))

    print("EVENTS:", events)
    print("START:", start_date, start_date.tzinfo)
    print("TASK DEADLINES:", [t.deadline for t in tasks])
    return events



# Эндпоинт для получения деталей конкретного события
@router.get("/events/{event_id}")
async def get_event_details(
    event_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    # ---------- MEETING ----------
    if event_id.startswith("meeting:"):
        meeting_id = int(event_id.split(":")[1])

        query = (
            select(Meeting)
            .join(MeetingParticipant)
            .where(
                Meeting.id == meeting_id,
                MeetingParticipant.user_id == current_user.id,
            )
        )
        meeting = (await db.execute(query)).scalar_one_or_none()
        if not meeting:
            raise HTTPException(404, "Meeting not found")

        participants = [str(p.user_id) for p in meeting.participants]
        now = datetime.now(timezone.utc)
        if meeting.is_cancelled:
            status = "cancelled"
        elif meeting.start_time <= now <= meeting.end_time:
            status = "in_progress"
        else:
            status = "planned"

        return {
            "id": event_id,
            "title": meeting.title,
            "description": "Встреча",
            "start_time": meeting.start_time.isoformat(),
            "end_time": meeting.end_time.isoformat(),
            "event_type": "meeting",
            "status": status,
            "team_id": str(meeting.team_id),
            "participants": participants,
        }

    # ---------- TASK ----------
    try:
        task_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(400, "Invalid event ID")

    task = await db.get(Task, task_uuid)
    if not task:
        raise HTTPException(404, "Task not found")

    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description or "",
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "status": task.status.value,
        "event_type": "task",
        "team_id": str(task.team_id),
    }
