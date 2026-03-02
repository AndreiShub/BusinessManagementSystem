from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from app.core.auth import fastapi_users, auth_backend
from app.db.models.task import Task
from app.db.session import get_db
from app.db.user_db import get_user_db
from app.schemas.users import UserRead, UserCreate, UserUpdate
from app.api.v1.teams import router as teams_router
from app.api.v1.team_members import router as team_members_router
from app.api.v1.tasks import router as tasks_router
from sqlalchemy.ext.asyncio import AsyncSession

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
    db: AsyncSession = Depends(get_db)
):
    """
    Возвращает задачи за указанный месяц.
    Если год и месяц не указаны, возвращает задачи за текущий месяц.
    """
    # Если год и месяц не указаны, используем текущие
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month
    
    # Создаем даты начала и конца месяца для фильтрации
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    # Запрос к БД для получения задач в указанном месяце
    query = select(Task).where(
        Task.deadline >= start_date,
        Task.deadline < end_date
    )
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Преобразуем задачи в формат, понятный фронтенду
    events = []
    for task in tasks:
        # Определяем тип события (по умолчанию task)
        event_type = "task"
        
        # Если у задачи есть deadline, используем его
        if task.deadline:
            event_date = task.deadline.date()
            event_time = task.deadline.time().strftime("%H:%M") if task.deadline.time() else None
        else:
            # Если дедлайна нет, можно пропустить задачу или установить текущую дату
            continue
        
        # Создаем событие для календаря
        event = {
            "id": str(task.id),
            "title": task.title,
            "description": task.description or "",
            "event_type": event_type,
            "date": event_date.isoformat(),
            "time": event_time,
            "status": task.status.value if task.status else None,
            "assignee_id": str(task.assignee_id) if task.assignee_id else None,
            "team_id": str(task.team_id)
        }
        events.append(event)
    
    return events

# Эндпоинт для получения деталей конкретной задачи
@router.get("/events/{event_id}")
async def get_event_details(
    event_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получает детальную информацию о задаче."""
    try:
        task_uuid = uuid.UUID(event_id)
        query = select(Task).where(Task.id == task_uuid)
        result = await db.execute(query)
        task = result.scalar_one_or_none()
        
        if task:
            return {
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "deadline": task.deadline.isoformat() if task.deadline else None,
                "status": task.status.value,
                "assignee": str(task.assignee_id) if task.assignee_id else None,
                "creator": str(task.creator_id)
            }
        return {"error": "Event not found"}
    except ValueError:
        return {"error": "Invalid event ID"}