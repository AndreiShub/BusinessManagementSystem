from app.repositories.me import MeRepository


class MeService:
    def __init__(self, repo: MeRepository):
        self.repo = repo

    async def update_me(self, user_update, user, user_db):
        updated = False

        if user_update.email is not None:
            user.email = user_update.email
            updated = True

        if user_update.nickname is not None:
            user.nickname = user_update.nickname
            updated = True

        if updated:
            await self.repo.update(user_db, user)

        return {
            "email": user.email,
            "nickname": user.nickname,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "is_manager": user.is_manager,
        }
