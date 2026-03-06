import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

from app.core.config import settings
from app.db.base import Base
import app.db.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# ------------------------------------------------
# Получаем URL базы
# ------------------------------------------------
def get_database_url():
    x_args = context.get_x_argument(as_dictionary=True)
    return x_args.get("db_url", settings.DATABASE_URL)


# ------------------------------------------------
# Offline migrations
# ------------------------------------------------
def run_migrations_offline():
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------
# Sync wrapper
# ------------------------------------------------
def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------------------------
# Online migrations (async)
# ------------------------------------------------
async def run_migrations_online():
    connectable = create_async_engine(
        get_database_url(),
        poolclass=None,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
