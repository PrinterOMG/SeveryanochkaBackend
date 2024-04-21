from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException, UploadFile

from api.dependencies import get_current_user, UsersServiceDep
from api.schemas.other import ErrorMessage
from api.schemas.user import UserRead, UserCheckResult, UserUpdate, SetAvatarResult
from core.exceptions.user import (
    BirthdayCanBeChangedOnceError,
    BadAvatarResolutionError,
    BadAvatarSizeError,
    BadAvatarTypeError,
)
from database.models import User

router = APIRouter(prefix='/users', tags=['Users'])


@router.get(
    '/me',
    response_model=UserRead,
    responses={401: {'description': 'Unauthorized', 'model': ErrorMessage}},
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Returns the current user for the passed access token
    """
    return current_user


@router.get(
    '/check',
    response_model=UserCheckResult,
    responses={404: {'description': 'User not found', 'model': ErrorMessage}},
)
async def check_user(
    user_service: UsersServiceDep, phone: Annotated[str, Query(pattern=r'^\+7\d{10}$')]
):
    """
    Checks whether the user exists using the provided phone number
    """
    user = await user_service.get_by_phone(phone)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User with provided phone number not found',
        )

    return {'success': True}


@router.put(
    '/me',
    responses={
        400: {
            'description': 'Birthday can be changed just once',
            'model': ErrorMessage,
        },
        401: {'description': 'Bad token', 'model': ErrorMessage},
    },
)
async def update_me(
    *,
    current_user: Annotated[User, Depends(get_current_user)],
    users_service: UsersServiceDep,
    user_update: UserUpdate,
) -> UserRead:
    """
    Updates the current user

    * Birthday can be changed just once
    """
    try:
        user = await users_service.update(current_user, user_update)
    except BirthdayCanBeChangedOnceError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Birthday can be changed just once',
        ) from error

    return user


@router.post(
    '/me/avatar',
    response_model=SetAvatarResult,
    responses={
        400: {
            'description': 'Something bad with avatar file. Check detail',
            'model': ErrorMessage,
        }
    },
)
async def set_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    avatar: UploadFile,
    user_service: UsersServiceDep,
):
    """
    Upload a new avatar to current user

    Avatar requirements:
    * File must be an image file .png or .jpeg
    * Image size must be no more than 10 MB
    * Image resolution should be no more than 1200x1200

    After adding a new avatar, the old one is completely deleted
    """
    try:
        avatar_url = await user_service.set_avatar(
            current_user=current_user, avatar=avatar
        )
    except BadAvatarResolutionError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Image resolution should be no more than 400x400',
        ) from error
    except BadAvatarSizeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Image size must be no more than 10 MB',
        ) from error
    except BadAvatarTypeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='File must be an image file (.png or .jpeg)',
        ) from error

    return SetAvatarResult(avatar_url=avatar_url)


@router.delete('/me/avatar', status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    current_user: Annotated[User, Depends(get_current_user)],
    user_service: UsersServiceDep,
):
    await user_service.delete_avatar(current_user)
