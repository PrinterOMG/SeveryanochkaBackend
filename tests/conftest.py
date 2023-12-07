import asyncio
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.base import Base, get_async_session, get_async_sessionmaker
from main import app
from settings import settings


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
def client() -> Generator[TestClient, None, None]:
    """
    Overrides the normal database access with test database,
    and yields a configured test client
    """

    app.dependency_overrides[get_async_sessionmaker] = override_get_async_sessionmaker

    with TestClient(app) as test_client:
        yield test_client


engine_test = create_async_engine(settings.test_database_connection_str, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_async_sessionmaker():
    return async_session_maker
