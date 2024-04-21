import uuid

import pytest
from httpx import AsyncClient

from database.models import Brand
from tests.conftest import client, async_session_maker

API_PREFIX = '/brands'


@pytest.mark.parametrize('limit, offset', [(1, 0), (20, 0), (10, 10), (10, 40)])
async def test_get_brands(prepared_brands: list[Brand], limit, offset):
    response = client.get(f'{API_PREFIX}?limit={limit}&offset={offset}')

    assert response.status_code == 200, response.status_code

    brands = response.json()

    for brand in prepared_brands[offset : offset + limit]:
        brand_data = {'id': str(brand.id), 'name': brand.name}

        assert brand_data in brands


async def test_get_brand(prepared_brands: list[Brand]):
    brand = prepared_brands[0]

    response = client.get(f'{API_PREFIX}/{brand.id}')

    assert response.status_code == 200, response.status_code

    brand_data = response.json()

    assert brand_data['id'] == str(brand.id)
    assert brand_data['name'] == brand.name


async def test_get_bad_brand():
    response = client.get(f'{API_PREFIX}/{uuid.uuid4()}')

    assert response.status_code == 404, response.status_code


async def test_create_brand(superuser_client: AsyncClient):
    body = {'name': 'abc'}

    response = await superuser_client.post(API_PREFIX, json=body)

    assert response.status_code == 201, response.status_code

    brand = response.json()

    async with async_session_maker() as session:
        db_brand = await session.get(Brand, brand['id'])

    assert db_brand is not None

    assert db_brand.name == body['name']


@pytest.mark.parametrize('body', [{'name': 'ab'}, {}, {'extra': 123}])
async def test_create_brand_bad_body(body: dict, superuser_client: AsyncClient):
    response = await superuser_client.post(API_PREFIX, json=body)

    assert response.status_code == 422, response.status_code


async def test_update_brand(
    prepared_brands: list[Brand], superuser_client: AsyncClient
):
    prepared_brand = prepared_brands[0]

    body = {'name': 'test brand'}

    response = await superuser_client.put(
        f'{API_PREFIX}/{prepared_brand.id}', json=body
    )

    assert response.status_code == 200, response.status_code

    brand = response.json()

    async with async_session_maker() as session:
        db_brand = await session.get(Brand, prepared_brand.id)

    assert db_brand is not None

    assert brand['name'] == body['name'] and brand['name'] == db_brand.name


async def test_update_bad_brand(superuser_client: AsyncClient):
    body = {'name': 'test brand'}

    response = await superuser_client.put(f'{API_PREFIX}/{uuid.uuid4()}', json=body)

    assert response.status_code == 404, response.status_code


@pytest.mark.parametrize('body', [{'name': 'ab'}, {}, {'extra': '123'}])
async def test_update_brand_bad_body(
    body: dict, prepared_brands: list[Brand], superuser_client: AsyncClient
):
    prepared_brand = prepared_brands[0]

    response = await superuser_client.put(
        f'{API_PREFIX}/{prepared_brand.id}', json=body
    )

    assert response.status_code == 422, response


async def test_delete_brand(
    prepared_brands: list[Brand], superuser_client: AsyncClient
):
    brand = prepared_brands[0]

    response = await superuser_client.delete(f'{API_PREFIX}/{brand.id}')

    assert response.status_code == 204, response.status_code

    async with async_session_maker() as session:
        db_brand = await session.get(Brand, brand.id)

    assert db_brand is None


async def test_delete_bad_brand(superuser_client: AsyncClient):
    response = await superuser_client.delete(f'{API_PREFIX}/{uuid.uuid4()}')

    assert response.status_code == 204, response.status_code
