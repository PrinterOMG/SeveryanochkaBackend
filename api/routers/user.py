from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException

from api.dependencies import get_current_user, UOWDep
from api.schemas.other import ErrorMessage
from api.schemas.user import UserRead, UserCheckResult
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
async def check_user(uow: UOWDep, phone: Annotated[str, Query(regex=r'^\+7\d{10}$')]):
    """
    Checks whether the user exists using the provided phone number
    """
    async with uow:
        user = await uow.users.get_by_phone(phone)

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User with provided phone number not found')

    return {'success': True}
