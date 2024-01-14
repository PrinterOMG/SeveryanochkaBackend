from datetime import datetime, timedelta

import pytest
from sqlalchemy import select

from database.models import PhoneKey
from tests.conftest import async_session_maker, client


BAD_PHONES = [
    '1234567890',
    '',
    '123',
    '+123-456-7890',
    '+7111111111111',
    '+89307229334'
]


@pytest.mark.parametrize('phone', BAD_PHONES)
async def test_create_bad_phone(phone: str):
    body = {
        'phone': phone
    }

    response = client.post('/api/phone_key/create', json=body)

    assert response.status_code == 422

    stmt = select(PhoneKey)
    async with async_session_maker() as session:
        records = await session.execute(stmt)
        phone_keys = records.scalars().all()

    assert len(phone_keys) == 0


async def test_create_rate_limit():
    body = {'phone': '+70000000000'}

    for _ in range(3):
        response = client.post('/api/phone_key/create', json=body)
        assert response.status_code == 201

    response = client.post('/api/phone_key/create', json=body)
    assert response.status_code == 429


async def test_create_success():
    body = {
        'phone': '+79307229334'
    }

    response = client.post('/api/phone_key/create', json=body)
    assert response.status_code == 201, response.text
    result = response.json()

    async with async_session_maker() as session:
        stmt = select(PhoneKey).where(PhoneKey.key == result['key'])
        record = await session.execute(stmt)
        db_phone_key = record.scalar_one()

    assert db_phone_key is not None


@pytest.mark.parametrize(
    'expires_at, is_verified',
    [
        (datetime.utcnow() + timedelta(minutes=15), False)
    ],
    ids=['Not verified and not expired']
)
async def test_verify_success(prepared_phone_key: PhoneKey):
    body = {
        'phone_key': prepared_phone_key.key,
        'code': '0000'
    }

    response = client.post('/api/phone_key/verify', json=body)

    assert response.status_code == 200

    result = response.json()

    assert result['is_verified'] is True

    async with async_session_maker() as session:
        db_phone_key = await session.get(PhoneKey, prepared_phone_key.id)
        assert db_phone_key.is_verified is True


@pytest.mark.parametrize(
    'expires_at, is_verified',
    [
        (datetime.utcnow() + timedelta(minutes=15), False)
    ],
    ids=['Not verified and not expired']
)
async def test_verify_bad_code(prepared_phone_key: PhoneKey):
    body = {
        'phone_key': prepared_phone_key.key,
        'code': '1111'
    }

    response = client.post('/api/phone_key/verify', json=body)

    assert response.status_code == 401

    async with async_session_maker() as session:
        db_phone_key = await session.get(PhoneKey, prepared_phone_key.id)
        assert db_phone_key.is_verified is False


async def test_verify_invalid_phone_key():
    body = {
        'phone_key': 'invalid_key',
        'code': '0000'
    }

    response = client.post('/api/phone_key/verify', json=body)

    assert response.status_code == 400


@pytest.mark.parametrize(
    'expires_at, is_verified',
    [
        (datetime.utcnow() + timedelta(minutes=15), True),
        (datetime.utcnow() - timedelta(minutes=15), False),
        (datetime.utcnow() - timedelta(minutes=15), True)
    ],
    ids=[
        'Verified, not expired',
        'Not verified, expired',
        'Verified, expired'
    ]
)
async def test_verify_bad_phone_key(prepared_phone_key: PhoneKey):
    body = {
        'phone_key': prepared_phone_key.key,
        'code': '0000'
    }

    response = client.post('/api/phone_key/verify', json=body)

    assert response.status_code == 400


@pytest.mark.parametrize(
    'expires_at, is_verified',
    [
        (datetime.utcnow() + timedelta(minutes=15), False)
    ],
    ids=[
        'Not verified, not expired'
    ]
)
async def test_get_success(prepared_phone_key: PhoneKey):
    response = client.get(f'/api/phone_key/{prepared_phone_key.key}')

    assert response.status_code == 200

    result = response.json()

    assert result['key'] == prepared_phone_key.key
    assert result['phone'] == prepared_phone_key.phone
    assert result['is_verified'] == prepared_phone_key.is_verified


async def test_get_invalid_phone_key():
    response = client.get('/api/phone_key/invalid_key')

    assert response.status_code == 404
