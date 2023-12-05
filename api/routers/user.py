from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import get_current_user
from api.schemas.user import UserRead
from database.models import User

router = APIRouter(prefix='/user', tags=['User'])


@router.get('/me', response_model=UserRead)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Returns the current user for the passed access token
    """
    return current_user
