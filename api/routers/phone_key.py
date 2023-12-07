import uuid
from datetime import timedelta, datetime
from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status

from api.dependencies import UOWDep
from api.schemas.other import ErrorMessage
from api.schemas.phone_key import PhoneKeyRead, CreatePhoneKey, VerifyPhoneKey
from database.models import PhoneKey

router = APIRouter(prefix='/phone_key', tags=['Phone verification key'])


@router.get(
    '/{phone_key}',
    responses={
        404: {
            'description': 'Key not found',
            'model': ErrorMessage
        }
    }
)
async def get_phone_key(
        phone_key: Annotated[str, Path(title='Phone key', description='Phone key')],
        uow: UOWDep
) -> PhoneKeyRead:
    async with uow:
        phone_key = await uow.phone_key.get_by_key(phone_key)
        if phone_key is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Key is invalid')

    return phone_key


@router.post(
    '/create',
    status_code=status.HTTP_201_CREATED,
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
    '/verify',
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
        phone_key = await uow.phone_key.get_by_key(request.phone_key)
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
