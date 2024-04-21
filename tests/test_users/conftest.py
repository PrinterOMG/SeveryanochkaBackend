from datetime import date
from tempfile import NamedTemporaryFile

import pytest
from PIL import Image

from database.models import User
from tests.conftest import async_session_maker


@pytest.fixture(scope='function')
async def prepared_user(
    phone: str,
    hashed_password: str,
    first_name: str,
    last_name: str,
    birthday: date,
    is_superuser: bool,
) -> User:
    new_user = User(
        phone=phone,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        birthday=birthday,
        is_superuser=is_superuser,
    )

    async with async_session_maker.begin() as session:
        session.add(new_user)

    yield new_user

    async with async_session_maker.begin() as session:
        await session.delete(new_user)


@pytest.fixture(scope='function')
def prepared_image(size: tuple[int, int], extension: str) -> Image:
    new_image = Image.new('RGB', size, (255, 255, 255, 0))

    file = NamedTemporaryFile(suffix=f'.{extension}')
    new_image.save(file, format=extension.upper())

    return file
