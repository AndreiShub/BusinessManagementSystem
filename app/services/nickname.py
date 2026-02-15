import random
import re
import time
from coolname import generate_slug


class NicknameService:
    def __init__(
        self,
        user_db,
        *,
        words: int = 2,
        max_number: int = 999,
        max_attempts: int = 5,
    ):
        self.user_db = user_db
        self.words = words
        self.max_number = max_number
        self.max_attempts = max_attempts

    def generate_nickname(self) -> str:
        base = generate_slug(self.words)
        number = random.randint(1, self.max_number)
        return f"{base}-{number}"

    def generate_nickname_from_email(self, email: str, max_length: int = 30) -> str:
        local = email.split("@")[0].lower()
        local = re.sub(r"[^a-z0-9_]", "", local)
        local = f"{local}_{random.randint(1, self.max_number)}"

        if len(local) < 3:
            local = f"user{random.randint(100, self.max_number)}"

        return local[:max_length]

    async def generate_nickname_unique(self, email: str) -> str:
        for attempt in range(self.max_attempts):
            if attempt < 3:
                nickname = self.generate_nickname()
            else:
                nickname = self.generate_nickname_from_email(email)
            if not await self.user_db.is_nickname_taken(nickname):
                return nickname
        timestamp = int(time.time())
        return f"user-{timestamp}"
