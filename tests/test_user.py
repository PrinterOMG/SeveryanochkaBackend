from datetime import date

import pytest
from httpx import AsyncClient
from fastapi.encoders import jsonable_encoder

from database.models import User
from tests.conftest import async_session_maker, client


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser, expires_minutes',
    [
        ('+71234567890', '123', None, None, None, False, 60)
    ],
    ids=['Base user']
)
async def test_user_delete(prepared_user: User, authenticated_client: AsyncClient):
    response = await authenticated_client.delete('/api/user/me')

    assert response.status_code == 204

    async with async_session_maker() as session:
        db_user = await session.get(User, prepared_user.id)

    assert db_user is None


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser, expires_minutes',
    [
        ('+71234567890', '123', None, None, None, False, 60)
    ],
    ids=['Base user']
)
async def test_user_get(prepared_user: User, authenticated_client: AsyncClient):
    response = await authenticated_client.get('/api/user/me')

    assert response.status_code == 200

    result = response.json()

    assert result['id'] == prepared_user.id


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser, expires_minutes',
    [
        ('+71234567890', '123', None, 'Olegov', None, False, 60)
    ],
    ids=['Base user']
)
async def test_user_patch_success(prepared_user: User, authenticated_client: AsyncClient):
    data = {
        'first_name': 'Oleg',
        'birthday': date(year=1999, month=1, day=1)
    }

    response = await authenticated_client.patch('/api/user/me', json=jsonable_encoder(data))

    assert response.status_code == 200, response.text

    result = response.json()

    async with async_session_maker() as session:
        db_user = await session.get(User, prepared_user.id)

    assert db_user is not None
    assert db_user.id == result['id']

    assert db_user.first_name == data['first_name'] and result['first_name'] == data['first_name']
    assert db_user.last_name == 'Olegov' and result['last_name'] == 'Olegov'
    assert db_user.birthday == data['birthday'] and date.fromisoformat(result['birthday']) == data['birthday']


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser, expires_minutes',
    [
        ('+71234567890', '123', None, None, date(1999, 1, 1), False, 60)
    ],
    ids=['User with birthday']
)
async def test_user_patch_bad_birthday_change(prepared_user: User, authenticated_client: AsyncClient):
    data = {
        'birthday': date(year=2000, month=1, day=1)
    }

    response = await authenticated_client.patch('/api/user/me', json=jsonable_encoder(data))

    assert response.status_code == 400, response.text

    async with async_session_maker() as session:
        db_user = await session.get(User, prepared_user.id)

    assert db_user is not None
    assert db_user.birthday == date(year=1999, month=1, day=1)


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser, expires_minutes',
    [
        ('+71234567890', '123', 'Oleg', 'Olegov', None, False, 60)
    ],
    ids=['Base user']
)
async def test_user_patch_bad_json(prepared_user: User, authenticated_client: AsyncClient):
    data = {}

    response = await authenticated_client.patch('/api/user/me', json=jsonable_encoder(data))

    assert response.status_code == 400, response.text

    async with async_session_maker() as session:
        db_user = await session.get(User, prepared_user.id)

    assert db_user is not None
    assert db_user.phone == '+71234567890'
    assert db_user.first_name == 'Oleg'
    assert db_user.last_name == 'Olegov'


@pytest.mark.parametrize(
    'phone, hashed_password, first_name, last_name, birthday, is_superuser',
    [
        ('+71234567890', '123', 'Oleg', 'Olegov', None, False)
    ],
    ids=['Base user']
)
async def test_check_user_success(prepared_user: User):
    response = client.get('/api/user/check', params={'phone': '+71234567890'})

    assert response.status_code == 200, response.text
    assert response.json()['success'] is True


async def test_check_bad_user():
    response = client.get('/api/user/check', params={'phone': '+71234567890'})

    assert response.status_code == 404, response.text
