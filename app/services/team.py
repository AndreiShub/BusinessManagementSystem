import secrets
from fastapi import HTTPException
from app.db.models.team import Team
from app.db.models.team_member import TeamMember, TeamRole
from sqlalchemy.future import select
from app.repositories.team import TeamRepository


class TeamService:
    def __init__(self, repo: TeamRepository):
        self.repo = repo

    async def create_team(self, session, data, user):
        # генерируем код
        code = secrets.token_hex(4)

        team = Team(name=data.name, code=code)

        team = await self.repo.create(session, team)

        # создаём администратора
        member = TeamMember(
            user_id=user.id,
            team_id=team.id,
            role=TeamRole.admin,
        )

        await self.repo.add_member(session, member)

        await self.repo.commit(session)

        return team

    async def list_teams(self, session, user):
        return await self.repo.get_user_teams(session, user.id)

    async def get_team(self, session, team_id, user):
        team = await self.repo.get_team_by_id(session, team_id)

        if not team:
            raise HTTPException(404, "Team not found")

        # проверка, что пользователь в команде
        result = await session.execute(
            select(TeamMember).where(
                TeamMember.team_id == team_id,
                TeamMember.user_id == user.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(403, "Not a team member")

        return team
