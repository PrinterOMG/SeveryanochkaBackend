from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.repositories.brand import SABrandRepository
from core.repositories.category import SACategoryRepository
from core.repositories.country import SACountryRepository
from core.repositories.manufacturer import SAManufacturerRepository
from core.repositories.phone_key import SAPhoneKeyRepository
from core.repositories.user import SAUserRepository
from database.base import get_async_session


def get_brand_repository(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return SABrandRepository(session)


def get_user_repository(session: Annotated[AsyncSession, Depends(get_async_session)]):
    return SAUserRepository(session)


def get_phone_key_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return SAPhoneKeyRepository(session)


def get_country_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return SACountryRepository(session)


def get_manufacturer_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return SAManufacturerRepository(session)


def get_category_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return SACategoryRepository(session)
