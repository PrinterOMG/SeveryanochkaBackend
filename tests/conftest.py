import gettext
from datetime import timedelta
from typing import AsyncGenerator

import pycountry
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.base import Base, get_async_session_factory
from database.models import User, Country
from main import app
from core.security import create_access_token


pytest_plugins = ['tests.docker_services']


DATABASE_URL_TEST = 'postgresql+asyncpg://test:secret-password@localhost:5432/test'

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


def override_get_session_factory():
    return async_session_maker


app.dependency_overrides[get_async_session_factory] = override_get_session_factory


@pytest.fixture(autouse=True, scope='session')
async def prepare_database(postgres_service):
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        russian = gettext.translation('iso3166-1', pycountry.LOCALES_DIR, languages=['ru'])

        countries = list()
        for country in pycountry.countries:
            countries.append({'name': russian.gettext(country.name), 'code': country.alpha_2})

        stmt = insert(Country).values(countries)
        await conn.execute(stmt)

    yield

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


client = TestClient(app)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def prepared_superuser() -> User:
    superuser = User(phone='phone', hashed_password='admin', is_superuser=True)

    async with async_session_maker.begin() as session:
        session.add(superuser)

    yield superuser

    async with async_session_maker.begin() as session:
        await session.delete(superuser)


def get_auth_headers(user: User, expires_minutes: int = 60) -> dict:
    access_token = create_access_token(
        data={'sub': str(user.id)}, expires_delta=timedelta(minutes=expires_minutes)
    )

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    return headers


@pytest.fixture(scope='function')
async def auth_headers(prepared_user: User, expires_minutes: int) -> dict:
    return get_auth_headers(prepared_user, expires_minutes)


@pytest.fixture(scope='function')
async def authenticated_client(auth_headers: dict) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test', headers=auth_headers) as ac:
        yield ac


@pytest.fixture(scope='function')
async def superuser_headers(prepared_superuser: User) -> dict:
    return get_auth_headers(prepared_superuser)


@pytest.fixture(scope='function')
async def superuser_client(superuser_headers: dict) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test', headers=superuser_headers) as ac:
        yield ac
