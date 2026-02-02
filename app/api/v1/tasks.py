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
