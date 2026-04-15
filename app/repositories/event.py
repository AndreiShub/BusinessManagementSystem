from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.models.task import Task, TaskAssignee
from app.db.models.meeting import Meeting, MeetingParticipant


class EventRepository:
    # ===== TASKS =====
    async def get_user_tasks_in_range(self, session, user_id, start, end):
        query = (
            select(Task)
            .join(TaskAssignee, Task.id == TaskAssignee.task_id)
            .where(
                TaskAssignee.user_id == user_id,
                Task.deadline >= start,
                Task.deadline < end,
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_task_assignees(self, session, task_id):
        result = await session.execute(
            select(TaskAssignee.user_id).where(TaskAssignee.task_id == task_id)
        )
        return result.scalars().all()

    async def get_task_by_id(self, session, task_id):
        return await session.get(Task, task_id)

    # ===== MEETINGS =====
    async def get_user_meetings_in_range(self, session, user_id, start, end):
        query = (
            select(Meeting)
            .options(selectinload(Meeting.participants))
            .join(MeetingParticipant)
            .where(
                MeetingParticipant.user_id == user_id,
                Meeting.start_time >= start,
                Meeting.start_time < end,
            )
        )
        result = await session.execute(query)
        return result.scalars().all()

    async def get_meeting_for_user(self, session, meeting_id, user_id):
        query = (
            select(Meeting)
            .join(MeetingParticipant)
            .where(
                Meeting.id == meeting_id,
                MeetingParticipant.user_id == user_id,
            )
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
