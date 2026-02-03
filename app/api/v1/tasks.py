import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.task import Task
from app.db.models.team_member import TeamMember
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.core.auth import current_active_user
from app.core.task_permissions import ensure_can_manage_tasks
from app.core.task_permissions import ensure_can_update_task

router = APIRouter(prefix="/teams/{team_id}/tasks", tags=["tasks"])


@router.post("/", response_model=TaskRead)
async def create_task(
    team_id: uuid.UUID,
    data: TaskCreate,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    await ensure_can_manage_tasks(db, user.id, team_id)

    # проверка исполнителя
    if data.assignee_id:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == data.assignee_id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(400, "Assignee is not in the team")

    task = Task(
        **data.dict(exclude_unset=True),
        team_id=team_id,
        creator_id=user.id,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskUpdate,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.team_id == team_id,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    permission = await ensure_can_update_task(db, user.id, task)

    update_data = data.dict(exclude_unset=True)

    # исполнитель может менять только статус
    if permission == "status_only":
        update_data = {"status": update_data.get("status", task.status)}

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.team_id == team_id,
        )
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(404, "Task not found")

    if task.creator_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Only creator can delete the task",
        )

    await db.delete(task)
    await db.commit()
