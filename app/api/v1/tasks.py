import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models.task import Task, TaskRating, TaskComment
from app.db.models.team_member import TeamMember
from app.schemas.task import (
    TaskCreate,
    TaskRatingOut,
    TaskRead,
    TaskUpdate,
    TaskRatingCreate,
    TaskCommentCreate,
    TaskCommentOut,
)
from app.core.auth import current_active_user
from app.core.task_permissions import ensure_can_manage_tasks
from app.core.task_permissions import ensure_can_update_task

router = APIRouter(prefix="/teams", tags=["tasks"])


@router.get("/{team_id}/tasks", response_model=list[TaskRead])
async def list_tasks(
    team_id: uuid.UUID,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_db),
):
    # 1️⃣ Проверяем, что пользователь состоит в команде
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user.id,
        )
    )
    membership = result.scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=403, detail="Not a team member")

    # 2️⃣ Получаем задачи команды
    result = await db.execute(select(Task).where(Task.team_id == team_id))

    tasks = result.scalars().all()
    return tasks


@router.get("/{team_id}/tasks/{task_id}")
async def get_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.team_id == team_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@router.post("/{team_id}/tasks", response_model=TaskRead)
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
        **data.model_dump(exclude_unset=True),
        team_id=team_id,
        creator_id=user.id,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{team_id}/tasks/{task_id}", response_model=TaskRead)
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

    update_data = data.model_dump(exclude_unset=True)

    # исполнитель может менять только статус
    if permission == "status_only":
        update_data = {"status": update_data.get("status", task.status)}

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{team_id}/tasks/{task_id}", status_code=204)
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


@router.get("/{team_id}/tasks/{task_id}/rating")
async def get_my_rating(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    stmt = select(TaskRating).where(
        TaskRating.task_id == task_id,
        TaskRating.user_id == user.id,
    )

    result = await db.execute(stmt)
    rating = result.scalar_one_or_none()

    if not rating:
        return {"score": None}

    return {"score": rating.score}


@router.get(
    "/{team_id}/tasks/{task_id}/ratings",
    response_model=list[TaskRatingOut],
)
async def get_task_ratings(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(TaskRating).where(TaskRating.task_id == task_id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{team_id}/tasks/{task_id}/rating")
async def rate_task(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskRatingCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    stmt = select(TaskRating).where(
        TaskRating.task_id == task_id,
        TaskRating.user_id == user.id,
    )

    result = await db.execute(stmt)
    rating = result.scalar_one_or_none()

    if rating:
        rating.score = data.score
    else:
        rating = TaskRating(
            task_id=task_id,
            user_id=user.id,
            score=data.score,
        )
        db.add(rating)

    await db.commit()
    return {"status": "ok"}


@router.get(
    "/{team_id}/tasks/{task_id}/comments",
    response_model=list[TaskCommentOut],
)
async def get_comments(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(TaskComment)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at)
    )

    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/{team_id}/tasks/{task_id}/comments",
    response_model=TaskCommentOut,
)
async def add_comment(
    team_id: uuid.UUID,
    task_id: uuid.UUID,
    data: TaskCommentCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(current_active_user),
):
    comment = TaskComment(
        task_id=task_id,
        user_id=user.id,
        text=data.text,
    )

    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return comment
