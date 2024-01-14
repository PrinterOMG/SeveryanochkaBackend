from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException

from api.dependencies import get_current_user, UOWDep
from api.schemas.other import ErrorMessage
from api.schemas.user import UserRead, UserCheckResult, UserUpdate
from database.models import User

router = APIRouter(prefix='/user', tags=['User'])


@router.get(
    '/me',
    response_model=UserRead,
    responses={
        401: {
            'description': 'Unauthorized',
            'model': ErrorMessage
        }
    }
)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Returns the current user for the passed access token
    """
    return current_user


@router.get(
    '/check',
    response_model=UserCheckResult,
    responses={
        404: {
            'description': 'User not found',
            'model': ErrorMessage
        }
    }
)
async def check_user(uow: UOWDep, phone: Annotated[str, Query(pattern=r'^\+7\d{10}$')]):
    """
    Checks whether the user exists using the provided phone number
    """
    async with uow:
        user = await uow.users.get_by_phone(phone)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User with provided phone number not found')

    return {'success': True}


@router.patch(
    '/me',
    responses={
        400: {
            'description': 'At least one field is required',
            'model': ErrorMessage
        },
        401: {
            'description': 'Something wrong with access... Check detail',
            'model': ErrorMessage
        }
    },
)
async def update_me(
        *,
        phone_key: Annotated[str | None, Query(description='Required for update phone')] = None,
        current_user: Annotated[User, Depends(get_current_user)],
        uow: UOWDep,
        user_update: UserUpdate
) -> UserRead:
    """
    Updates the current user

    * For phone update phone key is required
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='At least one field is required')

    if update_data.get('phone'):
        if phone_key is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Phone key is required for phone update')

        async with uow:
            db_phone_key = await uow.phone_key.get_by_key(phone_key)

        if db_phone_key is None or db_phone_key.expires_at < datetime.utcnow() or not db_phone_key.is_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Phone key is invalid, expired or not verified')

    for field, value in update_data.items():
        setattr(current_user, field, value)

    async with uow:
        current_user = await uow.users.update(current_user)
        if phone_key is not None and db_phone_key is not None:
            await uow.phone_key.delete(db_phone_key.id)
        await uow.commit()

    return current_user


@router.delete(
    '/me',
    responses={
        401: {
            'description': 'Auth error',
            'model': ErrorMessage
        }
    },
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_me(current_user: Annotated[User, Depends(get_current_user)], uow: UOWDep):
    """
    Completely deletes current user
    """
    async with uow:
        await uow.users.delete(current_user.id)
        await uow.commit()
