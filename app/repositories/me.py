class MeRepository:
    async def update(self, user_db, user):
        return await user_db.update(user)
