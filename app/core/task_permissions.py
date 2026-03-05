import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.team_member import TeamMember, TeamRole
from app.db.models.task import Task


async def ensure_can_manage_tasks(db: AsyncSession, user_id: uuid.UUID, team_id: uuid.UUID):
    # Проверяем, является ли пользователь участником команды и имеет ли права
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    )
    member = result.scalar_one_or_none()
    
    if not member:
        raise HTTPException(403, "Not allowed to manage tasks")
    
    # Проверяем роль (если нужно)
    # if member.role not in ['admin', 'manager']:
    #     raise HTTPException(403, "Insufficient permissions")
    
    return member

async def ensure_can_update_task(
    db: AsyncSession,
    user_id,
    task: Task,
):
    # автор
    if task.creator_id == user_id:
        return

    # исполнитель — только статус
    if task.assignee_id == user_id:
        return "status_only"

    # админ / менеджер
    result = await db.execute(
        select(TeamMember).where(
            TeamMember.team_id == task.team_id,
            TeamMember.user_id == user_id,
            TeamMember.role.in_([TeamRole.admin, TeamRole.manager]),
        )
    )
    if result.scalar_one_or_none():
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not allowed to update this task",
    )
