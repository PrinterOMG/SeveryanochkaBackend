from datetime import datetime, timedelta, date
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.base import Base, get_async_session_factory
from database.models import PhoneKey, User
from main import app
from settings import settings
from utils.security import create_access_token

DATABASE_URL_TEST = settings.test_database_url.unicode_string()

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


def override_get_session_factory():
    return async_session_maker


app.dependency_overrides[get_async_session_factory] = override_get_session_factory


@pytest.fixture(autouse=True, scope='session')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


client = TestClient(app)


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def prepared_phone_key(expires_at: datetime, is_verified: bool) -> PhoneKey:
    new_phone_key = PhoneKey(
        key='test_key',
        phone='+79307229334',
        expires_at=expires_at,
        is_verified=is_verified
    )

    async with async_session_maker.begin() as session:
        session.add(new_phone_key)

    yield new_phone_key

    async with async_session_maker.begin() as session:
        await session.delete(new_phone_key)


@pytest.fixture(scope='function')
async def prepared_user(
        phone: str,
        hashed_password: str,
        first_name: str,
        last_name: str,
        birthday: date,
        is_superuser: bool
) -> User:
    new_user = User(
        phone=phone,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        birthday=birthday,
        is_superuser=is_superuser
    )

    async with async_session_maker.begin() as session:
        session.add(new_user)

    yield new_user

    async with async_session_maker.begin() as session:
        await session.delete(new_user)


@pytest.fixture(scope='function')
async def auth_headers(prepared_user: User, expires_minutes: int) -> dict:
    access_token = create_access_token(
        data={'sub': str(prepared_user.id)}, expires_delta=timedelta(minutes=expires_minutes)
    )

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    return headers

@pytest.fixture(scope='function')
async def authenticated_client(auth_headers: dict) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test', headers=auth_headers) as ac:
        yield ac
