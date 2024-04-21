import uuid

import pytest
from httpx import AsyncClient

from database.models import Manufacturer
from tests.conftest import client, async_session_maker


API_PREFIX = '/test_manufacturers'


@pytest.mark.parametrize('limit, offset', [(1, 0), (20, 0), (10, 10), (10, 40)])
def test_get_manufacturers(prepared_manufacturers: list[Manufacturer], limit, offset):
    response = client.get(f'{API_PREFIX}?limit={limit}&offset={offset}')

    assert response.status_code == 200, response.status_code

    manufacturers = response.json()

    for manufacturer in prepared_manufacturers[offset : offset + limit]:
        manufacturer_data = {'id': str(manufacturer.id), 'name': manufacturer.name}

        assert manufacturer_data in manufacturers


async def test_get_manufacturer(prepared_manufacturers: list[Manufacturer]):
    manufacturer = prepared_manufacturers[0]

    response = client.get(f'{API_PREFIX}/{manufacturer.id}')

    assert response.status_code == 200, response.status_code

    manufacturer_data = response.json()

    assert manufacturer_data['id'] == str(manufacturer.id)
    assert manufacturer_data['name'] == manufacturer.name


async def test_get_bad_manufacturer():
    response = client.get(f'{API_PREFIX}/{uuid.uuid4()}')

    assert response.status_code == 404, response.status_code


async def test_create_manufacturer(superuser_client: AsyncClient):
    body = {'name': 'manufacturer 123'}

    response = await superuser_client.post(API_PREFIX, json=body)

    assert response.status_code == 201, response.status_code

    manufacturer = response.json()

    async with async_session_maker() as session:
        db_manufacturer = await session.get(Manufacturer, manufacturer['id'])

    assert db_manufacturer is not None

    assert db_manufacturer.name == body['name']


@pytest.mark.parametrize('body', [{'name': 'ab'}, {}, {'extra': 123}])
async def test_create_manufacturer_bad_body(body: dict, superuser_client: AsyncClient):
    response = await superuser_client.post(API_PREFIX, json=body)

    assert response.status_code == 422, response.status_code


async def test_update_manufacturer(
    prepared_manufacturers: list[Manufacturer], superuser_client: AsyncClient
):
    prepared_manufacturer = prepared_manufacturers[0]

    body = {'name': 'test manufacturer'}

    response = await superuser_client.put(
        f'{API_PREFIX}/{prepared_manufacturer.id}', json=body
    )

    assert response.status_code == 200, response.status_code

    manufacturer = response.json()

    async with async_session_maker() as session:
        db_manufacturer = await session.get(Manufacturer, prepared_manufacturer.id)

    assert db_manufacturer is not None

    assert (
        manufacturer['name'] == body['name']
        and manufacturer['name'] == db_manufacturer.name
    )


async def test_update_bad_manufacturer(superuser_client: AsyncClient):
    body = {'name': 'test manufacturer'}

    response = await superuser_client.put(f'{API_PREFIX}/{uuid.uuid4()}', json=body)

    assert response.status_code == 404, response.status_code


@pytest.mark.parametrize('body', [{'name': 'ab'}, {}, {'extra': '123'}])
async def test_update_manufacturer_bad_body(
    prepared_manufacturers: list[Manufacturer],
    body: dict,
    superuser_client: AsyncClient,
):
    prepared_manufacturer = prepared_manufacturers[0]

    response = await superuser_client.put(
        f'{API_PREFIX}/{prepared_manufacturer.id}', json=body
    )

    assert response.status_code == 422, response


async def test_delete_manufacturer(
    prepared_manufacturers: list[Manufacturer], superuser_client: AsyncClient
):
    manufacturer = prepared_manufacturers[0]

    response = await superuser_client.delete(f'{API_PREFIX}/{manufacturer.id}')

    assert response.status_code == 204, response.status_code

    async with async_session_maker() as session:
        db_manufacturer = await session.get(Manufacturer, manufacturer.id)

    assert db_manufacturer is None


async def test_delete_bad_manufacturer(superuser_client: AsyncClient):
    response = await superuser_client.delete(f'{API_PREFIX}/{uuid.uuid4()}')

    assert response.status_code == 204, response.status_code
