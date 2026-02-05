import asyncio
from app.core.auth import get_user_manager_direct
from fastapi_users.exceptions import UserAlreadyExists
from app.schemas.users import UserCreate

async def main():
    email = input("Email: ").strip()
    password = input("Password: ").strip()

    async for user_manager in get_user_manager_direct():
        try:
            await user_manager.create(
                UserCreate(
                    email=email,
                    password=password,
                    is_superuser=True,
                    is_active=True,
                    is_manager=True,
                )
            )
            print("✅ Superuser created")
        except UserAlreadyExists:
            print("❌ User already exists")


if __name__ == "__main__":
    asyncio.run(main())
