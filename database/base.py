import uuid
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncAttrs,
    AsyncEngine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import get_settings, Settings


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


async def get_async_engine(settings: Annotated[Settings, Depends(get_settings)]):
    return create_async_engine(settings.database_url)


async def get_async_session_factory(
    engine: Annotated[AsyncEngine, Depends(get_async_engine)],
) -> async_sessionmaker:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session(
    async_session_factory: Annotated[
        async_sessionmaker, Depends(get_async_session_factory)
    ],
):
    async with async_session_factory() as session:
        yield session
