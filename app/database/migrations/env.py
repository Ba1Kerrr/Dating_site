import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv, find_dotenv

# Файл лежит в: /app/database/migrations/env.py
#
# /app/database/migrations/env.py
#        ↑              ↑
#  DATABASE_DIR     MIGRATIONS_DIR
#
# database.py лежит в /app/database/ → добавляем /app/database
# funcs/hash.py лежит в /app/        → добавляем /app

MIGRATIONS_DIR = os.path.dirname(os.path.abspath(__file__))          # /app/database/migrations
DATABASE_DIR   = os.path.dirname(MIGRATIONS_DIR)                     # /app/database
APP_DIR        = os.path.dirname(DATABASE_DIR)                       # /app

sys.path.insert(0, APP_DIR)       # чтобы найти funcs.hash
sys.path.insert(0, DATABASE_DIR)  # чтобы найти database.database

load_dotenv(find_dotenv("settings/.env"))

from database import metadata  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_ROUTE"])

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()