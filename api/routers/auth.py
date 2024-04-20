from typing import Annotated

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.dependencies import AuthServiceDep
from api.schemas.auth import TokenRead, RegisterRequest, ResetPasswordRequest
from api.schemas.other import ErrorMessage
from core.exceptions.auth import BadCredentialsError
from core.exceptions.base import EntityAlreadyExistsError, EntityNotFoundError
from core.exceptions.phone_key import BadPhoneKeyError


router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=TokenRead,
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
async def register(request: RegisterRequest, auth_service: AuthServiceDep):
    """
    Creates a new user.

    To complete this request you need a verified phone key
    """
    try:
        token = await auth_service.register_user(register_data=request)
    except BadPhoneKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Key is expired, invalid or used'
        ) from error
    except EntityAlreadyExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='User with provided phone number already exists'
        ) from error

    return token


@router.post(
    '/login',
    response_model=TokenRead,
    responses={
        401: {
            'description': 'Incorrect credentials',
            'model': ErrorMessage
        }
    }
)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: AuthServiceDep
):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect username or password',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        token = await auth_service.login_user(login_data=form_data)
    except BadCredentialsError as error:
        raise exception from error

    return token


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
async def reset_password(request: ResetPasswordRequest, auth_service: AuthServiceDep):
    try:
        await auth_service.reset_password(reset_data=request)
    except BadPhoneKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Key is expired, invalid or used'
        ) from error
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='User with provided phone does not exists'
        ) from error
