from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import Settings, get_settings
from core.entities.auth import TokenData
from core.entities.user import UserEntity
from core.services.auth import AuthServiceBase
from core.services.brand import BrandServiceBase
from core.services.category import CategoryServiceBase
from core.services.country import CountryServiceBase
from core.services.manufacturer import ManufacturerServiceBase
from core.services.phone_key import PhoneKeyServiceBase
from core.services.providers import (
    get_brand_service,
    get_user_service,
    get_phone_key_service,
    get_auth_service,
    get_country_service,
    get_manufacturer_service,
    get_category_service,
)
from core.services.user import UserServiceBase
from database.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/login')

BrandsServiceDep = Annotated[BrandServiceBase, Depends(get_brand_service)]
UsersServiceDep = Annotated[UserServiceBase, Depends(get_user_service)]
PhoneKeyServiceDep = Annotated[PhoneKeyServiceBase, Depends(get_phone_key_service)]
AuthServiceDep = Annotated[AuthServiceBase, Depends(get_auth_service)]
CountryServiceDep = Annotated[CountryServiceBase, Depends(get_country_service)]
ManufacturerServiceDep = Annotated[
    ManufacturerServiceBase, Depends(get_manufacturer_service)
]
CategoryServiceDep = Annotated[CategoryServiceBase, Depends(get_category_service)]

SettingsDep = Annotated[Settings, Depends(get_settings)]


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    users_service: UsersServiceDep,
    settings: SettingsDep,
) -> UserEntity:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        try:
            user_id = UUID(payload.get('sub'))
        except (ValueError, TypeError):
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    user = await users_service.get_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception

    return user


def current_user_id_admin(
    current_user: Annotated[User, Depends(get_current_user)],
) -> bool:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='You do not have permission to perform this',
        )

    return True
