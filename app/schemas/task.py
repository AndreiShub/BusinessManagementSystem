import uuid
from datetime import datetime
from pydantic import BaseModel
from app.db.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    assignee_id: uuid.UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None
    status: TaskStatus | None = None
    assignee_id: uuid.UUID | None = None


class TaskRead(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    deadline: datetime | None
    status: TaskStatus
    assignee_id: uuid.UUID | None

    class Config:
        from_attributes = True
