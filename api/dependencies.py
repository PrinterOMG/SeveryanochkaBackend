from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from api.schemas.auth import TokenData
from database.models import User
from settings import settings
from utils.unit_of_work import UnitOfWorkBase, UnitOfWork


UOWDep = Annotated[UnitOfWorkBase, Depends(UnitOfWork)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], uow: UOWDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get('sub')
        if user_id is None or not user_id.isdigit():
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception

    async with uow:
        user = await uow.users.get_by_id(token_data.user_id)

    if user is None:
        raise credentials_exception

    return user


def current_user_id_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='You do not have permission to perform this')

    return True
