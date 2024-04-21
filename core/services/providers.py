from typing import Annotated

from fastapi import Depends

from config import Settings, get_settings
from core.repositories.brand import BrandRepositoryBase
from core.repositories.category import CategoryRepositoryBase
from core.repositories.country import CountryRepositoryBase
from core.repositories.manufacturer import ManufacturerRepositoryBase
from core.repositories.phone_key import PhoneKeyRepositoryBase
from core.repositories.providers import (
    get_brand_repository,
    get_user_repository,
    get_phone_key_repository,
    get_country_repository,
    get_manufacturer_repository,
    get_category_repository,
)
from core.repositories.user import UserRepositoryBase
from core.services.auth import AuthService, AuthServiceBase
from core.services.brand import BrandService, BrandServiceBase
from core.services.category import CategoryServiceBase, CategoryService
from core.services.country import CountryService, CountryServiceBase
from core.services.manufacturer import ManufacturerService, ManufacturerServiceBase
from core.services.phone_key import PhoneKeyService, PhoneKeyServiceBase
from core.services.user import UserService, UserServiceBase
from core.unit_of_work import UnitOfWorkBase, get_uow


def get_brand_service(
    brand_repository: Annotated[BrandRepositoryBase, Depends(get_brand_repository)],
    uow: Annotated[UnitOfWorkBase, Depends(get_uow)],
) -> BrandServiceBase:
    return BrandService(brand_repository=brand_repository, uow=uow)


def get_user_service(
    user_repository: Annotated[UserRepositoryBase, Depends(get_user_repository)],
    uow: Annotated[UnitOfWorkBase, Depends(get_uow)],
) -> UserServiceBase:
    return UserService(user_repository=user_repository, uow=uow)


def get_phone_key_service(
    phone_key_repository: Annotated[
        PhoneKeyRepositoryBase, Depends(get_phone_key_repository)
    ],
    uow: Annotated[UnitOfWorkBase, Depends(get_uow)],
) -> PhoneKeyServiceBase:
    return PhoneKeyService(phone_key_repository=phone_key_repository, uow=uow)


def get_auth_service(
    user_service: Annotated[UserServiceBase, Depends(get_user_service)],
    phone_key_service: Annotated[PhoneKeyServiceBase, Depends(get_phone_key_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthServiceBase:
    return AuthService(
        user_service=user_service,
        phone_key_service=phone_key_service,
        settings=settings,
    )


def get_country_service(
    country_repository: Annotated[
        CountryRepositoryBase, Depends(get_country_repository)
    ],
) -> CountryServiceBase:
    return CountryService(country_repository=country_repository)


def get_manufacturer_service(
    manufacturer_repository: Annotated[
        ManufacturerRepositoryBase, Depends(get_manufacturer_repository)
    ],
    uow: Annotated[UnitOfWorkBase, Depends(get_uow)],
) -> ManufacturerServiceBase:
    return ManufacturerService(manufacturer_repository=manufacturer_repository, uow=uow)


def get_category_service(
    category_repository: Annotated[
        CategoryRepositoryBase, Depends(get_category_repository)
    ],
    uow: Annotated[UnitOfWorkBase, Depends(get_uow)],
) -> CategoryServiceBase:
    return CategoryService(category_repository=category_repository, uow=uow)
