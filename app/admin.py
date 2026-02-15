from sqladmin import Admin, ModelView
from fastapi import FastAPI
from app.db.session import engine
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from app.db.models import User, Team, Task, TeamMember
from app.core.auth import get_user_manager_direct
from typing import Callable, AsyncGenerator
from fastapi_users.exceptions import UserNotExists


class FastAPIUsersAdminAuth(AuthenticationBackend):
    def __init__(self, get_user_manager: Callable[[], AsyncGenerator]):
        self.get_user_manager = get_user_manager
        self.middlewares = []

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")

        try:
            user_manager = await anext(self.get_user_manager())
            user = await user_manager.get_by_email(email)
        except UserNotExists:
            return False

        valid, new_hash = user_manager.password_helper.verify_and_update(
            password,
            user.hashed_password,
        )

        if not valid or not user.is_superuser:
            return False

        request.session["user_id"] = str(user.id)
        request.session["is_superuser"] = True

        if new_hash:
            user.hashed_password = new_hash
            await user_manager.user_db.update(user)

        return True

    async def logout(self, request: Request) -> None:
        pass

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("user_id")
        return bool(user_id)


def setup_admin(app: FastAPI):
    admin = Admin(
        app,
        engine,
        title="My Admin Panel",
        authentication_backend=FastAPIUsersAdminAuth(get_user_manager_direct),
    )

    class UserAdmin(ModelView, model=User):
        column_list = [
        User.nickname,  # Ник на первом месте
        User.email,
        User.is_active,
        User.is_superuser,
        User.is_manager,
        User.id,  # UUID тоже показываем, но не на первом месте
    ]
    
    # Переименовываем колонки для красивого отображения
    column_labels = {
        User.nickname: "Nickname",
        User.email: "Email",
        User.is_active: "Active",
        User.is_superuser: "Superuser",
        User.is_manager: "Manager",
        User.id: "UUID",
    }
    
    # Сортировка по умолчанию по нику
    column_default_sort = [(User.nickname, True)]  # True для возрастания
    
    # Делаем ник кликабельным для перехода к деталям
    column_details_list = [
        User.nickname,
        User.email,
        User.id,
        User.is_active,
        User.is_superuser,
        User.is_manager,
    ]
    
    # Форматирование колонок
    column_formatters = {
        User.nickname: lambda m, a: f"@{m.nickname}"  # Добавляет @ перед ником
    }
    
    # Поиск по нику и email
    column_searchable_list = [
        User.nickname,
        User.email,
    ]
    
    # Фильтры
    column_filters = [
        User.is_active,
        User.is_superuser,
        User.is_manager,
    ]
    
    # Можно скрыть UUID из списка, если не нужен
    # column_list.remove(User.id)
    
    # Настройка имени в навигации
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    class TeamAdmin(ModelView, model=Team):
        pass

    class TaskAdmin(ModelView, model=Task):
        pass

    class TeamMemberAdmin(ModelView, model=TeamMember):
        pass

    admin.add_view(UserAdmin)
    admin.add_view(TeamAdmin)
    admin.add_view(TaskAdmin)
    admin.add_view(TeamMemberAdmin)
