from sqladmin import Admin, ModelView
from fastapi import FastAPI
from app.db.session import engine
from app.db.models import User, Team, Task, TeamMember


def setup_admin(app: FastAPI):
    admin = Admin(app, engine, title="My Admin Panel")

    class UserAdmin(ModelView, model=User):
        pass

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
