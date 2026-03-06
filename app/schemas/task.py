from typing import Annotated, List, Optional
import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from app.db.models.task import TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None
    assignee_ids: list[uuid.UUID] = []
    model_config = {"from_attributes": True}


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None
    status: TaskStatus | None = None
    assignee_id: uuid.UUID | None = None
    model_config = {"from_attributes": True}


class TaskRead(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str]
    deadline: datetime | None
    status: TaskStatus
    team_id: uuid.UUID
    assignee_ids: List[uuid.UUID]

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
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True
