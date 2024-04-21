import asyncio
import gettext
from logging.config import fileConfig

import pycountry
from sqlalchemy import pool, insert, select, func
from sqlalchemy.engine import Connection
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import async_engine_from_config, AsyncEngine

from alembic import context

from database.base import Base
from database.models import Country
from config import get_settings

settings = get_settings()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
config.set_main_option('sqlalchemy.url', settings.database_url)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option('sqlalchemy.url')
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def insert_default_countries(connectable: AsyncEngine) -> None:
    async with connectable.connect() as connection:
        stmt = select(func.count()).select_from(Country)
        try:
            result = await connection.scalar(stmt)
        except ProgrammingError:
            return

    if result == 0:
        russian = gettext.translation(
            'iso3166-1', pycountry.LOCALES_DIR, languages=['ru']
        )

        countries = list()
        for country in pycountry.countries:
            countries.append(
                {'name': russian.gettext(country.name), 'code': country.alpha_2}
            )

        async with connectable.connect() as connection:
            stmt = insert(Country).values(countries)
            await connection.execute(stmt)
            await connection.commit()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await insert_default_countries(connectable)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
