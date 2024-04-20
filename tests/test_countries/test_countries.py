import uuid

import pytest
from sqlalchemy import select

from database.models import Country
from tests.conftest import client, async_session_maker


API_PREFIX = '/countries'


@pytest.mark.parametrize(
    'offset, limit',
    [
        (0, 1), (0, 100), (20, 20)
    ]
)
async def test_get_countries(offset, limit):
    async with async_session_maker() as session:
        stmt = select(Country)
        countries = await session.scalars(stmt)
        db_countries = countries.all()

    response = client.get(f'{API_PREFIX}?offset={offset}&limit={limit}')

    assert response.status_code == 200, response.status_code

    countries = response.json()

    for country in db_countries[offset:offset + limit]:
        country_data = {
            'id': str(country.id),
            'code': country.code,
            'name': country.name
        }

        assert country_data in countries


async def test_get_country_by_id():
    async with async_session_maker() as session:
        stmt = select(Country).limit(1)
        db_country = await session.scalar(stmt)

    response = client.get(f'{API_PREFIX}/id/{db_country.id}')

    assert response.status_code == 200, response.status_code

    country = response.json()

    assert country['id'] == str(db_country.id)
    assert country['name'] == db_country.name
    assert country['code'] == db_country.code


async def test_get_country_by_bad_id():
    response = client.get(f'{API_PREFIX}/id/{uuid.uuid4()}')

    assert response.status_code == 404, response.status_code


async def test_get_country_by_code():
    async with async_session_maker() as session:
        stmt = select(Country).limit(1)
        db_country = await session.scalar(stmt)

    response = client.get(f'{API_PREFIX}/code/{db_country.code}')

    assert response.status_code == 200, response.status_code

    country = response.json()

    assert country['id'] == str(db_country.id)
    assert country['name'] == db_country.name
    assert country['code'] == db_country.code


async def test_get_country_by_bad_code():
    response = client.get(f'{API_PREFIX}/code/ABD')

    assert response.status_code == 404, response.status_code
