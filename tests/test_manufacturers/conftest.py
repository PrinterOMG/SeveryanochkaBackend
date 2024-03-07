import pytest
from sqlalchemy import text

from database.models import Manufacturer
from tests.conftest import async_session_maker


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
