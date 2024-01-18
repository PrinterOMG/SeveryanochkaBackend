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
            'description': 'Something bad... Check detail',
            'model': ErrorMessage
        },
        401: {
            'description': 'Bad token',
            'model': ErrorMessage
        }
    },
)
async def update_me(
        *,
        current_user: Annotated[User, Depends(get_current_user)],
        uow: UOWDep,
        user_update: UserUpdate
) -> UserRead:
    """
    Updates the current user

    * Birthday can be changed just once
    """
    update_data = user_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='At least one field is required')

    if update_data.get('birthday') and current_user.birthday:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Birthday can be changed just once')

    for field, value in update_data.items():
        setattr(current_user, field, value)

    async with uow:
        current_user = await uow.users.update(current_user)
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
