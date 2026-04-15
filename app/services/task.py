from fastapi import HTTPException
from sqlalchemy import select
from app.db.models.task import Task, TaskRating, TaskComment
from app.db.models.team_member import TeamMember
from app.repositories.task import TaskRepository
from app.schemas.task import TaskRead, TaskCommentOut
from app.core.task_permissions import ensure_can_manage_tasks
from app.core.task_permissions import ensure_can_update_task


class TaskService:
    def __init__(self, repo: TaskRepository):
        self.repo = repo

    # ===== TASKS =====

    async def get_team_tasks(self, session, team_id, user):
        # проверка команды
        member = await session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id,
            )
        )
        if not member.scalar_one_or_none():
            raise HTTPException(403, "Not a team member")

        tasks = await self.repo.get_team_tasks(session, team_id)

        # формируем ответ
        result = []
        for task in tasks:
            result.append(
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "deadline": task.deadline.isoformat() if task.deadline else None,
                    "status": task.status,
                    "team_id": task.team_id,
                    "assignee_ids": [a.user_id for a in task.assignees],
                }
            )

        return result

    async def get_task(self, session, team_id, task_id):
        task = await self.repo.get_by_id(session, task_id, team_id)

        if not task:
            raise HTTPException(404, "Task not found")

        return task

    async def create_task(self, session, team_id, data, user):
        await ensure_can_manage_tasks(session, user.id, team_id)

        # проверка участников
        for uid in data.assignee_ids:
            result = await session.execute(
                select(TeamMember).where(
                    TeamMember.team_id == team_id,
                    TeamMember.user_id == uid,
                )
            )
            if not result.scalar_one_or_none():
                raise HTTPException(400, f"User {uid} is not in the team")

        task = Task(
            title=data.title,
            description=data.description,
            deadline=data.deadline,
            team_id=team_id,
            creator_id=user.id,
        )

        task = await self.repo.create(session, task)

        await self.repo.add_assignees(session, task.id, data.assignee_ids)

        await self.repo.commit(session)

        task = await self.repo.get_with_assignees(session, task.id)

        return TaskRead(
            id=task.id,
            title=task.title,
            description=task.description,
            deadline=task.deadline.isoformat() if task.deadline else None,
            status=task.status.value if task.status else None,
            team_id=task.team_id,
            assignee_ids=[a.user_id for a in task.assignees],
        )

    async def update_task(self, session, team_id, task_id, data, user):
        task = await self.repo.get_by_id(session, task_id, team_id)

        if not task:
            raise HTTPException(404, "Task not found")

        permission = await ensure_can_update_task(session, user.id, task)

        update_data = data.model_dump(exclude_unset=True)

        if permission == "status_only":
            update_data = {"status": update_data.get("status", task.status)}

        for field, value in update_data.items():
            setattr(task, field, value)

        await self.repo.commit(session)
        await self.repo.refresh(session, task)

        return task

    async def delete_task(self, session, team_id, task_id, user):
        task = await self.repo.get_by_id(session, task_id, team_id)

        if not task:
            raise HTTPException(404, "Task not found")

        if task.creator_id != user.id:
            raise HTTPException(403, "Only creator can delete the task")

        await self.repo.delete(session, task)

    # ===== RATINGS =====

    async def get_my_rating(self, session, task_id, user):
        rating = await self.repo.get_user_rating(session, task_id, user.id)

        if not rating:
            return {"score": None}

        return {"score": rating.score}

    async def get_task_ratings(self, session, task_id):
        return await self.repo.get_task_ratings(session, task_id)

    async def rate_task(self, session, task_id, data, user):
        rating = await self.repo.get_user_rating(session, task_id, user.id)

        if rating:
            rating.score = data.score
        else:
            rating = TaskRating(
                task_id=task_id,
                user_id=user.id,
                score=data.score,
            )

        await self.repo.save_rating(session, rating)

        return {"status": "ok"}

    async def get_average_rating(self, session, task_id, start, end):
        avg = await self.repo.get_avg_rating_in_range(session, task_id, start, end)

        return {
            "task_id": str(task_id),
            "average_rating": float(avg) if avg is not None else None,
            "start": start.isoformat(),
            "end": end.isoformat(),
        }

    # ===== COMMENTS =====

    async def get_comments(self, session, task_id):
        rows = await self.repo.get_comments(session, task_id)

        return [
            TaskCommentOut(
                id=comment.id,
                text=comment.text,
                nickname=nickname,
                created_at=comment.created_at,
            )
            for comment, nickname in rows
        ]

    async def add_comment(self, session, task_id, data, user):
        comment = TaskComment(
            task_id=task_id,
            user_id=user.id,
            text=data.text,
        )

        return await self.repo.create_comment(session, comment)
