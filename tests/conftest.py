import asyncio
import gettext
import timeit
from datetime import datetime, timedelta, date
from typing import AsyncGenerator, Callable, Awaitable, Any

import asyncpg
import pycountry
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import text, insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from database.base import Base, get_async_session_factory
from database.models import PhoneKey, User, Category, Brand, Country, Manufacturer
from main import app
from settings import settings
from utils.security import create_access_token


DATABASE_URL_TEST = 'postgresql+asyncpg://test:secret-password@localhost:5432/test'

engine_test = create_async_engine(DATABASE_URL_TEST, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = engine_test


def override_get_session_factory():
    return async_session_maker


app.dependency_overrides[get_async_session_factory] = override_get_session_factory


async def postgres_responsive(host: str) -> bool:
    try:
        conn = await asyncpg.connect(
            host=host,
            port=5432,
            user='test',
            database='test',
            password='secret-password'
        )
    except (ConnectionError, asyncpg.CannotConnectNowError):
        return False

    try:
        return (await conn.fetchrow('SELECT 1'))[0] == 1
    finally:
        await conn.close()


async def async_wait_until_responsive(
    check: Callable[..., Awaitable],
    timeout: float,
    pause: float,
    **kwargs: Any,
) -> None:
    ref = timeit.default_timer()
    now = ref
    while (now - ref) < timeout:
        if await check(**kwargs):
            return
        await asyncio.sleep(pause)
        now = timeit.default_timer()

    raise RuntimeError('Timeout reached while waiting on service!')


@pytest.fixture(scope='session')
async def postgres_service(docker_services):
    await async_wait_until_responsive(
        timeout=30,
        pause=0.1,
        check=postgres_responsive,
        host='localhost'
    )


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
async def prepared_brands():
    brands = list()
    for i in range(1, 31):
        brands.append(Brand(name=f'Brand {i}'))

    async with async_session_maker.begin() as session:
        session.add_all(brands)

    yield brands

    async with async_session_maker.begin() as session:
        await session.execute(text(f'TRUNCATE TABLE {Brand.__tablename__} CASCADE;'))


@pytest.fixture(scope='function')
async def prepared_manufacturers():
    manufacturers = list()
    for i in range(1, 31):
        manufacturers.append(Manufacturer(name=f'Manufacturer {i}'))

    async with async_session_maker.begin() as session:
        session.add_all(manufacturers)

    yield manufacturers

    async with async_session_maker.begin() as session:
        await session.execute(text(f'TRUNCATE TABLE {Manufacturer.__tablename__} CASCADE;'))


@pytest.fixture(scope='function')
async def prepared_category():
    parent_category = Category(name='Мясо и птица')
    first_child_category = Category(name='Мясо', parent=parent_category)
    second_child_category = Category(name='Птица', parent=parent_category)

    async with async_session_maker.begin() as session:
        session.add_all((parent_category, first_child_category, second_child_category))

    yield parent_category

    async with async_session_maker.begin() as session:
        await session.execute(text(f'TRUNCATE TABLE {Category.__tablename__} CASCADE;'))


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
def prepared_image(size) -> Image:
    new_image = Image.new('RGBA', size, (255, 255, 255, 0))
    new_image.save('test.png')

    return new_image


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
