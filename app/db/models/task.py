import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID

from app.db.base import Base


class TaskStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    done = "done"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus),
        default=TaskStatus.open,
        nullable=False,
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="CASCADE"),
    )

    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
    )

    assignees = relationship(
        "TaskAssignee",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    team = relationship("Team")
    creator = relationship("User", foreign_keys=[creator_id])
    comments = relationship("TaskComment", backref="task", cascade="all, delete")
    ratings = relationship("TaskRating", backref="task", cascade="all, delete")


class TaskAssignee(Base):
    __tablename__ = "task_assignees"

    task_id = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )

    user = relationship("User")


class TaskRating(Base):
    __tablename__ = "task_ratings"

    id = Column(Integer, primary_key=True)
    task_id = Column(ForeignKey("tasks.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)

    score = Column(Integer, nullable=False)  # 1–5
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("task_id", "user_id", name="uq_task_user_rating"),
    )


class TaskComment(Base):
    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")
