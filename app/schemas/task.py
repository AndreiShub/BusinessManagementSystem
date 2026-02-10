from typing import Annotated
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
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


class TaskRatingCreate(BaseModel):
    score: Annotated[int, Field(ge=1, le=5)]


class TaskRatingOut(BaseModel):
    score: int
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class TaskCommentCreate(BaseModel):
    text: Annotated[str, Field(min_length=1, max_length=2000)]


class TaskCommentOut(BaseModel):
    id: int
    text: str
    user_id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
