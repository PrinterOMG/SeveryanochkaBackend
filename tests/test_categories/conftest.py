import pytest
from sqlalchemy import text

from database.models import Category
from tests.conftest import async_session_maker


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
