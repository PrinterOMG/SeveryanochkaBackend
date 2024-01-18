from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import UOWDep
from api.schemas.auth import Token, RegisterRequest, RegisterResult, ResetPasswordRequest
from api.schemas.other import ErrorMessage
from database.models.user import User
from settings import settings
from utils.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            'description': 'Provided phone key is expired, invalid or used',
            'model': ErrorMessage
        },
        409: {
            'description': 'User with provided phone number already exists',
            'model': ErrorMessage
        }
    }
)
async def register(request: RegisterRequest, uow: UOWDep) -> RegisterResult:
    """
    Creates a new user.

    To complete this request you need a verified phone key
    """
    async with uow:
        phone_key = await uow.phone_key.get_by_key(request.phone_key)
        if phone_key is None or (not phone_key.is_active):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Key is expired, invalid or used')

        existed_user = await uow.users.get_by_phone(phone_key.phone)
        if existed_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail='User with provided phone number already exists')

        hashed_password = get_password_hash(request.password)
        new_user = User(
            phone=phone_key.phone,
            hashed_password=hashed_password
        )
        new_user = await uow.users.add(new_user)

        phone_key.is_used = True
        phone_key.used_at = datetime.utcnow()
        await uow.phone_key.update(phone_key)

        await uow.commit()

    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    access_token = create_access_token(
        data={'sub': str(new_user.id)}, expires_delta=access_token_expires
    )

    return RegisterResult(
        user=new_user,
        token=Token(access_token=access_token)
    )


@router.post(
    '/login',
    responses={
        401: {
            'description': 'Incorrect credentials',
            'model': ErrorMessage
        }
    }
)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], uow: UOWDep) -> Token:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'Bearer'},
    )
    async with uow:
        user = await uow.users.get_by_phone(form_data.username)
        if user is None:
            raise exception

        if not verify_password(form_data.password, user.hashed_password):
            raise exception

    access_token_expires = timedelta(minutes=settings.access_token_expires_minutes)
    access_token = create_access_token(
        data={'sub': str(user.id)}, expires_delta=access_token_expires
    )

    return Token(access_token=access_token)


@router.post(
    '/reset_password',
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {
            'description': 'Phone key is expired, invalid or used',
            'model': ErrorMessage
        },
        400: {
            'description': 'User with provided phone does not exists',
            'model': ErrorMessage
        }
    }
)
async def reset_password(request: ResetPasswordRequest, uow: UOWDep):
    async with uow:
        phone_key = await uow.phone_key.get_by_key(request.phone_key)
        if phone_key is None or (not phone_key.is_active):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Key is expired, invalid or used')

        user = await uow.users.get_by_phone(phone_key.phone)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='User with provided phone does not exists')

        user.hashed_password = get_password_hash(request.password)
        await uow.users.update(user)

        phone_key.is_used = True
        phone_key.used_at = datetime.utcnow()
        await uow.phone_key.update(phone_key)

        await uow.commit()
