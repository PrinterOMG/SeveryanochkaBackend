from datetime import datetime

import pytest

from database.models import PhoneKey
from tests.conftest import async_session_maker


@pytest.fixture(scope='function')
async def prepared_phone_key(expires_at: datetime, is_verified: bool) -> PhoneKey:
    new_phone_key = PhoneKey(
        key='test_key',
        phone='+79307229334',
        expires_at=expires_at,
        is_verified=is_verified
    )

    async with async_session_maker.begin() as session:
        session.add(new_phone_key)

    yield new_phone_key

    async with async_session_maker.begin() as session:
        await session.delete(new_phone_key)
