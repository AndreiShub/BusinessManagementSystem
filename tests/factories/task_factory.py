import uuid
from app.db.models import Task


async def create_task(db_session, **kwargs):

    task = Task(
        id=uuid.uuid4(),
        title=kwargs.get("title", "Test task"),
        description=kwargs.get("description", "Test description"),
        team_id=kwargs.get("team_id"),
        creator_id=kwargs.get("creator_id"),
    )

    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)

    return task