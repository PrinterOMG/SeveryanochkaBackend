import uuid
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Path, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import UOWDep
from api.schemas.auth import Token, RegisterRequest, RegisterResult, VerifyPhoneKey, CreatePhoneKey, PhoneKeyRead
from api.schemas.other import ErrorMessage
from database.models import PhoneKey
from database.models.user import User
from settings import settings
from utils.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.get(
    '/phone_key/{key}', tags=['Phone key'],
    responses={
        404: {
            'description': 'Key not found',
            'model': ErrorMessage
        }
    }
)
async def get_phone_key(
        key: Annotated[str, Path(title='Phone key', description='Phone key')],
        uow: UOWDep
) -> PhoneKeyRead:
    async with uow:
        phone_key = await uow.phone_key.get_by_key(key)
        if phone_key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Key is invalid')

    return phone_key


@router.post(
    '/phone_key/create',
    tags=['Phone key'],
    responses={
        429: {
            'description': 'Too many create requests (limit is 3 per hour)',
            'model': ErrorMessage
        }
    }
)
async def create_phone_key(request: CreatePhoneKey, uow: UOWDep) -> PhoneKeyRead:
    """
    Creates a key for requests with a phone number confirmation.

    For one phone number, you can create only 3 keys per hour.

    Unverified phone key is valid for only 15 minutes (and 10 minutes after verification).
    During these 15 minutes you need to have time to verify the key so that you can carry out an operation with it

    The key will need to be verified with the `/auth/verify_phone_key` request

    * (During development, any four-digit code will be valid and nothing is sent to the user's phone number)
    """
    async with uow:
        phone_keys = await uow.phone_key.get_last_hour_keys_by_phone(request.phone)
        if len(phone_keys) >= 3:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                                detail='The request limit (3 per hour) for this number has been exceeded')

        key = str(uuid.uuid4())  # Получение ключа от стороннего сервиса
        expire_date = datetime.utcnow() + timedelta(minutes=15)
        new_phone_key = PhoneKey(
            key=key,
            phone=request.phone,
            expires_at=expire_date
        )
        new_phone_key = await uow.phone_key.add(new_phone_key)

        await uow.commit()

    return new_phone_key


@router.post(
    '/phone_key/verify',
    tags=['Phone key'],
    responses={
        400: {
            'description': 'Key is expired, invalid or already exists',
            'model': ErrorMessage
        }
    }
)
async def verify_phone_key(request: VerifyPhoneKey, uow: UOWDep) -> PhoneKeyRead:
    """
    Verifies the phone key so that you can then use it to perform an operation like registration or password reset

    The verified key is one-time use and is valid for only 10 minutes. After use, the key is completely deleted

    * (During development, any four-digit code will be valid and nothing is sent to the user's phone number)
    """
    async with uow:
        phone_key = await uow.phone_key.get_by_key(request.key)
        if phone_key is None or phone_key.expires_at < datetime.utcnow() or phone_key.is_verified:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Key is expired, invalid or already verified')

        is_correct_code = True  # Проверка кода через сторонний сервис
        if not is_correct_code:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Confirmation code is invalid')

        phone_key.is_verified = True
        phone_key.expires_at = datetime.utcnow() + timedelta(minutes=10)
        phone_key = await uow.phone_key.update(phone_key)

    return phone_key


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            'description': 'Provided phone key is expired or invalid',
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
        if phone_key is None or phone_key.expires_at < datetime.utcnow():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Key is expired or invalid')

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

        await uow.phone_key.delete(phone_key.id)

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
