from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Depends, HTTPException, status

from api.dependencies import current_user_id_admin, CategoryServiceDep
from api.schemas.category import CategoryRead, CategoryCreate, CategoryUpdate
from api.schemas.other import ErrorMessage
from core.exceptions.base import EntityNotFoundError


router = APIRouter(prefix='/categories', tags=['Categories'])


@router.get('/')
async def get_categories(
        category_service: CategoryServiceDep,
        depth: Annotated[int, Query(ge=0, description='Depth of returned subcategories')] = 1
) -> list[CategoryRead]:
    """
    Return all root categories with their `child`.

    Whether children will be obtained from a category depends on the `depth` parameter.
    Root categories have `depth` 0, their `child` have `depth` 1, and so on.
    If the `depth` for `child` of a certain category exceeds the passed `depth` parameter,
    then `child` of this category will not be received (`child` will be always an empty list)
    """
    return await category_service.get_root_categories(depth)


@router.get('/{category_id}')
async def get_category(
        category_service: CategoryServiceDep,
        category_id: UUID,
        depth: Annotated[int, Query(ge=0, description='Depth of returned subcategories')] = 1
) -> CategoryRead:
    """
    Return category with provided `id` with its `child`.

    Whether children will be obtained from a category depends on the `depth` parameter.
    Root categories have `depth` 0, their `child` have `depth` 1, and so on.
    If the `depth` for `child` of a certain category exceeds the passed `depth` parameter,
    then `child` of this category will not be received (`child` will be always an empty list)
    """
    category = await category_service.get_by_id(category_id, depth=depth)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Category with id {category_id} does not exist'
        )

    return category


@router.post(
    '/',
    dependencies=[Depends(current_user_id_admin)],
    response_model=CategoryRead,
    status_code=201,
    responses={
        400: {
            'model': ErrorMessage,
            'description': 'Bad parent_id'
        }
    }
)
async def create_category(category_service: CategoryServiceDep, new_category: CategoryCreate):
    """
    Create a new category. Categories can have the same names

    * Requires superuser privileges
    """
    return await category_service.create(new_category)


@router.put(
    '/{category_id}',
    dependencies=[Depends(current_user_id_admin)],
    response_model=CategoryRead,
    responses={
        404: {
            'model': ErrorMessage,
            'description': 'Category with provided id does not exist'
        },
        400: {
            'model': ErrorMessage,
            'description': 'Bad parent_id'
        }
    }
)
async def update_category(category_service: CategoryServiceDep, category_id: UUID, category_update: CategoryUpdate):
    """
    Update a category with provided `category_id`

    * Sub-categories depth is always 0, so child will be always empty list
    * Requires superuser privileges
    """
    try:
        return await category_service.update(category_id, category_update)
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Category with id {error.find_query} does not exist'
        ) from error


@router.delete(
    '/{category_id}',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'model': ErrorMessage,
            'description': 'Category with provided id does not exists'
        }
    }
)
async def delete_category(category_service: CategoryServiceDep, category_id: UUID) -> None:
    """
    Delete category with provided `category_id`

    * Requires superuser privileges
    """
    await category_service.delete(category_id)
