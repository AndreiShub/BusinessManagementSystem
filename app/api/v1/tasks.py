import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.user import User
from app.db.session import get_db
from app.db.models.task import Task, TaskAssignee, TaskRating, TaskComment
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


# list_tasks
@router.get("/{team_id}/tasks")
async def get_team_tasks(
    team_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user)
):
    # Проверяем, что пользователь в команде
    member = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == current_user.id
        )
    )
    if not member.scalar_one_or_none():
        raise HTTPException(403, "Not a team member")
    
    # Получаем задачи команды с загрузкой исполнителей
    result = await db.execute(
        select(Task)
        .where(Task.team_id == team_id)
        .options(selectinload(Task.assignees))  # 👈 ВАЖНО: загружаем исполнителей
    )
    tasks = result.scalars().all()
    
    # Формируем ответ с исполнителями
    task_list = []
    for task in tasks:
        # Собираем ID исполнителей
        assignee_ids = [a.user_id for a in task.assignees]
        
        task_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "status": task.status,
            "team_id": task.team_id,
            "assignee_ids": assignee_ids,  # 👈 Теперь здесь будут ID
        })
    
    return task_list


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

    # проверяем всех исполнителей
    for uid in data.assignee_ids:
        result = await db.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == uid
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(400, f"User {uid} is not in the team")

    # создаем задачу
    task = Task(
        title=data.title,
        description=data.description,
        deadline=data.deadline,
        team_id=team_id,
        creator_id=user.id,
    )
    db.add(task)
    await db.flush()

    # добавляем всех исполнителей
    for uid in data.assignee_ids:
        db.add(TaskAssignee(task_id=task.id, user_id=uid))

    await db.commit()
    
    # ВАЖНО: Делаем новый запрос с загрузкой отношений
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignees))  # явно загружаем исполнителей
        .where(Task.id == task.id)
    )
    task_with_assignees = result.scalar_one()

    # получаем список ID исполнителей
    assignee_ids = [a.user_id for a in task_with_assignees.assignees]

    return TaskRead(
        id=task_with_assignees.id,
        title=task_with_assignees.title,
        description=task_with_assignees.description,
        deadline=task_with_assignees.deadline.isoformat() if task_with_assignees.deadline else None,
        status=task_with_assignees.status.value if task_with_assignees.status else None,
        team_id=task_with_assignees.team_id,
        assignee_ids=assignee_ids
    )

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
        select(TaskComment, User.nickname)
        .join(User, TaskComment.user_id == User.id)
        .where(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at)
    )

    result = await db.execute(stmt)

    return [
        TaskCommentOut(
            id=comment.id,
            text=comment.text,
            nickname=nickname,
            created_at=comment.created_at,
        )
        for comment, nickname in result.all()
    ]


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
