import pytest
from sqlalchemy import text

from database.models import Brand
from tests.conftest import async_session_maker


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
