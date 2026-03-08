import uuid

from app.db.models import Task
from app.db.models.task import TaskAssignee, TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(
    db_session: AsyncSession,
    title: str,
    team_id: uuid.UUID,
    creator_id: uuid.UUID,
    description: str | None = None,
    status: TaskStatus = TaskStatus.open,
    assignee_ids: list[uuid.UUID] | None = None,
) -> Task:
    task = Task(
        title=title,
        description=description,
        status=status,
        team_id=team_id,
        creator_id=creator_id,
    )

    if assignee_ids:
        for user_id in assignee_ids:
            task.assignees.append(TaskAssignee(user_id=user_id))

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    return task
