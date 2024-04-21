from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, status

from api.dependencies import PhoneKeyServiceDep
from api.schemas.other import ErrorMessage
from api.schemas.phone_key import PhoneKeyRead, CreatePhoneKey, VerifyPhoneKey
from core.exceptions.phone_key import (
    PhoneKeyCreateLimitError,
    BadPhoneKeyError,
    BadConfirmationCodeError,
)

router = APIRouter(prefix='/phone_keys', tags=['Phone verification key'])


@router.get(
    '/{key}',
    response_model=PhoneKeyRead,
    responses={404: {'description': 'Key not found', 'model': ErrorMessage}},
)
async def get_phone_key(
    key: Annotated[str, Path(title='Key', description='Key')],
    phone_key_service: PhoneKeyServiceDep,
):
    phone_key = await phone_key_service.get_by_key(key)

    if phone_key is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Key is invalid'
        )

    return phone_key


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=PhoneKeyRead,
    responses={
        429: {
            'description': 'Too many create requests (limit is 3 per hour)',
            'model': ErrorMessage,
        },
        530: {'description': 'SMS service unavailable', 'model': ErrorMessage},
    },
)
async def create_phone_key(
    request: CreatePhoneKey, phone_key_service: PhoneKeyServiceDep
):
    """
    Creates a key for requests with a phone number confirmation.

    For one phone number, you can create only 3 keys per hour.

    Unverified phone key is valid for only 15 minutes (and 10 minutes after verification).
    During these 15 minutes you need to have time to verify the key so that you can carry out an operation with it

    The key will need to be verified with the `/auth/verify_phone_key` request
    """
    try:
        phone_key = await phone_key_service.create(request.phone)
    except PhoneKeyCreateLimitError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail='The request limit (3 per hour) for this number has been exceeded',
        ) from error

    return phone_key


@router.post(
    '/verify',
    responses={
        400: {
            'description': 'Key is expired, invalid or already exists',
            'model': ErrorMessage,
        },
        401: {'description': 'Confirmation code is invalid', 'model': ErrorMessage},
    },
)
async def verify_phone_key(
    request: VerifyPhoneKey, phone_key_service: PhoneKeyServiceDep
) -> PhoneKeyRead:
    """
    Verifies the phone key so that you can then use it to perform an operation like registration or password reset

    The verified key is one-time use and is valid for only 10 minutes.

    * (During development, the code 0000 will always be correct and nothing is sent to the user's phone number)
    """
    try:
        phone_key = await phone_key_service.verify(key=request.key, code=request.code)
    except BadPhoneKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Key is expired, invalid or already verified',
        ) from error
    except BadConfirmationCodeError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Confirmation code {error.confirmation_code} is invalid',
        ) from error

    return phone_key
