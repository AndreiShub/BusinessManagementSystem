from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.db.models.user import User
from app.db.models.task import Task, TaskAssignee, TaskRating, TaskComment


class TaskRepository:
    # ===== TASKS =====

    async def get_team_tasks(self, session, team_id):
        result = await session.execute(
            select(Task)
            .where(Task.team_id == team_id)
            .options(selectinload(Task.assignees))
        )
        return result.scalars().all()

    async def get_by_id(self, session, task_id, team_id):
        result = await session.execute(
            select(Task).where(Task.id == task_id, Task.team_id == team_id)
        )
        return result.scalar_one_or_none()

    async def create(self, session, task: Task):
        session.add(task)
        await session.flush()
        return task

    async def add_assignees(self, session, task_id, user_ids):
        for uid in user_ids:
            session.add(TaskAssignee(task_id=task_id, user_id=uid))

    async def delete(self, session, task: Task):
        await session.delete(task)
        await session.commit()

    async def commit(self, session):
        await session.commit()

    async def refresh(self, session, obj):
        await session.refresh(obj)

    async def get_with_assignees(self, session, task_id):
        result = await session.execute(
            select(Task).options(selectinload(Task.assignees)).where(Task.id == task_id)
        )
        return result.scalar_one()

    # ===== RATINGS =====

    async def get_user_rating(self, session, task_id, user_id):
        stmt = select(TaskRating).where(
            TaskRating.task_id == task_id,
            TaskRating.user_id == user_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_task_ratings(self, session, task_id):
        stmt = select(TaskRating).where(TaskRating.task_id == task_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def save_rating(self, session, rating: TaskRating):
        session.add(rating)
        await session.commit()

    async def get_avg_rating_in_range(self, session, task_id, start, end):
        result = await session.execute(
            select(func.avg(TaskRating.score)).where(
                TaskRating.task_id == task_id,
                TaskRating.created_at >= start,
                TaskRating.created_at < end,
            )
        )
        return result.scalar()

    # ===== COMMENTS =====

    async def get_comments(self, session, task_id):
        stmt = (
            select(TaskComment, User.nickname)
            .join(User, TaskComment.user_id == User.id)
            .where(TaskComment.task_id == task_id)
            .order_by(TaskComment.created_at)
        )
        result = await session.execute(stmt)
        return result.all()

    async def create_comment(self, session, comment: TaskComment):
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment
