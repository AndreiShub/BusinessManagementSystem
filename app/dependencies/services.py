from fastapi import Depends
from app.repositories.event import EventRepository
from app.repositories.me import MeRepository
from app.repositories.meeting import MeetingRepository
from app.services.event import EventService
from app.services.me import MeService
from app.services.meeting import MeetingService
from app.repositories.task import TaskRepository
from app.services.task import TaskService
from app.repositories.team_member import TeamMemberRepository
from app.services.team_member import TeamMemberService
from app.repositories.team import TeamRepository
from app.services.team import TeamService


def get_meeting_repository():
    return MeetingRepository()


def get_meeting_service(
    repo: MeetingRepository = Depends(get_meeting_repository),
):
    return MeetingService(repo)


def get_task_repository():
    return TaskRepository()


def get_task_service(
    repo: TaskRepository = Depends(get_task_repository),
):
    return TaskService(repo)


def get_team_member_repository():
    return TeamMemberRepository()


def get_team_member_service(
    repo: TeamMemberRepository = Depends(get_team_member_repository),
):
    return TeamMemberService(repo)


def get_team_repository():
    return TeamRepository()


def get_team_service(
    repo: TeamRepository = Depends(get_team_repository),
):
    return TeamService(repo)


def get_event_repository():
    return EventRepository()


def get_event_service(
    repo: EventRepository = Depends(get_event_repository),
):
    return EventService(repo)


def get_me_repository():
    return MeRepository()


def get_me_service(
    repo: MeRepository = Depends(get_me_repository),
):
    return MeService(repo)
