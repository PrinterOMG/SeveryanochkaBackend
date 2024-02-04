import pytest
from httpx import AsyncClient

from database.models import Category
from tests.conftest import client, async_session_maker


async def test_get_categories_depth_0(prepared_category: Category):
    response = client.get('/api/category?depth=0')

    assert response.status_code == 200, response.status_code

    json_response = response.json()

    assert len(json_response) == 1
    category = json_response[0]
    assert category['name'] == prepared_category.name
    assert category['parent_id'] == prepared_category.parent_id
    assert category['child'] == []


@pytest.mark.parametrize(
    'url',
    ['/api/category?depth=1', '/api/category'],
    ids=['depth=1', 'without depth']
)
async def test_get_categories_depth_1(prepared_category: Category, url: str):
    response = client.get(url)

    assert response.status_code == 200, response.status_code

    json_response = response.json()

    assert len(json_response) == 1
    category = json_response[0]
    assert category['name'] == prepared_category.name
    assert category['parent_id'] == prepared_category.parent_id
    assert len(category['child']) == len(prepared_category.child)


@pytest.mark.parametrize(
    'depth',
    [-1, 'abc'],
    ids=['-1', 'abc']
)
async def test_get_categories_bad_depth(depth):
    response = client.get('/api/category?depth={depth}')

    assert response.status_code == 422, response.status_code


async def test_get_category_depth_0(prepared_category: Category):
    response = client.get(f'/api/category/{prepared_category.id}?depth=0')

    assert response.status_code == 200, response.status_code

    category = response.json()

    assert category['name'] == prepared_category.name
    assert category['parent_id'] == prepared_category.parent_id
    assert len(category['child']) == 0


@pytest.mark.parametrize(
    'url',
    ['/api/category/{category_id}?depth=1', '/api/category/{category_id}'],
    ids=['depth=1', 'without depth']
)
async def test_get_category_depth_1(prepared_category: Category, url):
    response = client.get(url.format(category_id=prepared_category.id))

    assert response.status_code == 200, response.status_code

    category = response.json()

    assert category['name'] == prepared_category.name
    assert category['parent_id'] == prepared_category.parent_id
    assert len(category['child']) == len(prepared_category.child)


def test_get_bad_category():
    response = client.get('/api/category/123')

    assert response.status_code == 404, response.status_code


@pytest.mark.parametrize(
    'depth',
    [(-1, ), ('abc', )],
    ids=['-1', 'abc']
)
def test_get_category_bad_depth(depth):
    # Category with id 123 does not exist in this context, but here it doesn't matter
    response = client.get('/api/category/123?depth={depth}')

    assert response.status_code == 422, response.status_code


async def create_test_category(parent_id: int | None, client: AsyncClient) -> tuple[dict, Category]:
    body = {
        'name': 'test_category',
        'parent_id': parent_id
    }

    response = await client.post('/api/category/', json=body)

    assert response.status_code == 201, response.status_code

    category = response.json()

    async with async_session_maker() as session:
        db_category = await session.get(Category, category['id'])
        for sub_category in await db_category.awaitable_attrs.child:
            await session.refresh(sub_category)

    assert db_category is not None

    assert category['name'] == body['name'] and body['name'] == db_category.name
    assert category['parent_id'] == body['parent_id'] and body['parent_id'] == db_category.parent_id

    return category, db_category


async def test_create_category_without_parent(superuser_client: AsyncClient):
    _, db_category = await create_test_category(parent_id=None, client=superuser_client)

    assert len(db_category.child) == 0


async def test_create_category_with_parent(prepared_category: Category, superuser_client: AsyncClient):
    # prepared_category will be parent category for new category
    _, db_category = await create_test_category(parent_id=prepared_category.id, client=superuser_client)

    child_count_before = len(prepared_category.child)

    async with async_session_maker() as session:
        prepared_category = await session.get(Category, prepared_category.id)
        await session.refresh(prepared_category, ['child'])

    assert child_count_before + 1 == len(prepared_category.child)


async def test_create_category_with_bad_parent(superuser_client: AsyncClient):
    body = {
        'name': 'test_category',
        'parent_id': 123
    }

    response = await superuser_client.post('/api/category/', json=body)

    assert response.status_code == 400, response.status_code


@pytest.mark.parametrize(
    'body',
    [
        {'name': 'test_category'},
        {'parent_id': 123},
        {}
    ],
    ids=['Without parent_id', 'Without name', 'Empty']
)
async def test_create_category_with_bad_body(body: dict, superuser_client: AsyncClient):
    response = await superuser_client.post('/api/category/', json=body)

    assert response.status_code == 422, response.status_code


async def test_update_category_name(prepared_category: Category, superuser_client: AsyncClient):
    body = {
        'name': 'test_category edited'
    }

    response = await superuser_client.patch(f'/api/category/{prepared_category.id}', json=body)

    assert response.status_code == 200, response.status_code

    edited_category = response.json()

    assert edited_category['name'] == body['name']
    assert edited_category['parent_id'] == prepared_category.parent_id

    async with async_session_maker() as session:
        db_category = await session.get(Category, prepared_category.id)
        for sub_category in await db_category.awaitable_attrs.child:
            await session.refresh(sub_category)

    assert len(db_category.child) == len(prepared_category.child)


async def test_update_category_all(prepared_category: Category, superuser_client: AsyncClient):
    first_child = prepared_category.child[0]

    body = {
        'name': 'test_category edited',
        'parent_id': None
    }

    response = await superuser_client.patch(f'/api/category/{first_child.id}', json=body)

    assert response.status_code == 200, response.status_code

    edited_category = response.json()

    assert edited_category['name'] == body['name']
    assert edited_category['parent_id'] == body['parent_id']

    async with async_session_maker() as session:
        db_category = await session.get(Category, prepared_category.id)
        for sub_category in await db_category.awaitable_attrs.child:
            await session.refresh(sub_category)

    assert len(db_category.child) == len(prepared_category.child) - 1


async def test_update_bad_category(superuser_client: AsyncClient):
    body = {
        'name': 'test_category edited'
    }

    response = await superuser_client.patch('/api/category/123', json=body)

    assert response.status_code == 404, response.status_code


async def test_delete_category(prepared_category: Category, superuser_client: AsyncClient):
    response = await superuser_client.delete(f'/api/category/{prepared_category.id}')

    assert response.status_code == 204, response.status_code

    async with async_session_maker() as session:
        db_category = await session.get(Category, prepared_category.id)
        first_child = await session.get(Category, prepared_category.child[0].id)
        second_child = await session.get(Category, prepared_category.child[1].id)

    assert db_category is None
    assert first_child is not None and second_child is not None
    assert first_child.parent_id is None and second_child.parent_id is None


async def test_delete_bad_category(superuser_client: AsyncClient):
    response = await superuser_client.delete('/api/category/123')

    assert response.status_code == 404, response.status_code
