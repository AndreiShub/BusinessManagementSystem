from datetime import datetime
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.user import User
from app.db.session import get_db
from app.dependencies.services import get_task_service
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskRatingCreate,
    TaskCommentCreate,
)
from app.core.auth import current_active_user
from app.services.task import TaskService

router = APIRouter(prefix="/teams", tags=["tasks"])


@router.get("/{team_id}/tasks")
async def get_team_tasks(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_team_tasks(db, team_id, user)


@router.get("/{team_id}/tasks/{task_id}")
async def get_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_task(db, team_id, task_id)


@router.post("/{team_id}/tasks")
async def create_task(
    team_id: uuid.UUID,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.create_task(db, team_id, data, user)


@router.patch("/{team_id}/tasks/{task_id}")
async def update_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.update_task(db, team_id, task_id, data, user)


@router.delete("/{team_id}/tasks/{task_id}")
async def delete_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.delete_task(db, team_id, task_id, user)


@router.get("/{team_id}/tasks/{task_id}/rating")
async def get_my_rating(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_my_rating(db, task_id, user)


@router.get("/{team_id}/tasks/{task_id}/ratings")
async def get_task_ratings(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_task_ratings(db, task_id)


@router.post("/{team_id}/tasks/{task_id}/rating")
async def rate_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskRatingCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.rate_task(db, task_id, data, user)


@router.get("/{team_id}/tasks/{task_id}/average-rating")
async def get_task_average_rating(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    start: datetime,
    end: datetime,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_average_rating(db, task_id, start, end)


@router.get("/{team_id}/tasks/{task_id}/comments")
async def get_comments(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    service: TaskService = Depends(get_task_service),
):
    return await service.get_comments(db, task_id)


@router.post("/{team_id}/tasks/{task_id}/comments")
async def add_comment(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
    service: TaskService = Depends(get_task_service),
):
    return await service.add_comment(db, task_id, data, user)
