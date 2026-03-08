import uuid

from app.db.models import Task
from app.db.models.task import TaskAssignee, TaskStatus
from sqlalchemy.ext.asyncio import AsyncSession


async def create_task(db_session, team_id, creator_id, **kwargs):
    task = Task(
        id=uuid.uuid4(),
        title=kwargs.get("title", f"Task {uuid.uuid4().hex[:6]}"),
        description=kwargs.get("description", "Test task"),
        team_id=team_id,
        creator_id=creator_id,
        status=TaskStatus.in_progress,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task
