from fastapi import HTTPException
from app.db.models.team_member import TeamMember, TeamRole
from app.repositories.team_member import TeamMemberRepository


class TeamMemberService:
    def __init__(self, repo: TeamMemberRepository):
        self.repo = repo

    async def join_team(self, session, code, user):
        # 1. команда
        team = await self.repo.get_team_by_code(session, code)

        if not team:
            raise HTTPException(404, "Team not found")

        # 2. уже в команде?
        membership = await self.repo.get_membership(
            session,
            team.id,
            user.id,
        )

        if membership:
            raise HTTPException(400, "You are already a member")

        # 3. создаём
        member = TeamMember(
            user_id=user.id,
            team_id=team.id,
            role=TeamRole.user,
        )

        await self.repo.create_member(session, member)

        return {"message": "Joined the team successfully"}

    async def get_team_members(self, session, team_id):
        rows = await self.repo.get_team_members(session, team_id)

        result = []
        for tm, user in rows:
            result.append(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "nickname": user.nickname or user.email,
                    },
                    "role": tm.role,
                }
            )

        return result
