from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException, status

from api.dependencies import UOWDep, current_user_id_admin
from api.schemas.category import CategoryRead, CategoryCreate, CategoryUpdate
from api.schemas.other import ErrorMessage
from database.models import Category


router = APIRouter(prefix='/category', tags=['Category'])


async def refresh_sub_categories(uow, category: Category, max_depth: int, cur_depth=0):
    """
    To limit the depth, the attribute 'child' is cleared, so it's better to call after commit if it occurs
    """
    if cur_depth >= max_depth:
        await category.awaitable_attrs.child
        category.child = []
        return

    for sub_category in await category.awaitable_attrs.child:
        await uow.refresh(sub_category)
        await refresh_sub_categories(uow, sub_category, max_depth, cur_depth + 1)


@router.get('/')
async def get_categories(
        uow: UOWDep,
        depth: Annotated[int, Query(ge=0, description='Depth of returned subcategories')] = 1
) -> list[CategoryRead]:
    """
    Return all root categories with their `child`.

    Whether children will be obtained from a category depends on the `depth` parameter.
    Root categories have `depth` 0, their `child` have `depth` 1, and so on.
    If the `depth` for `child` of a certain category exceeds the passed `depth` parameter,
    then `child` of this category will not be received (`child` will be always an empty list)
    """
    async with uow:
        root_categories = await uow.category.list(parent_id=None)

        for category in root_categories:
            await refresh_sub_categories(uow, category, max_depth=depth)

    return root_categories


@router.get('/{category_id}')
async def get_category(
        uow: UOWDep,
        category_id: int,
        depth: Annotated[int, Query(ge=0, description='Depth of returned subcategories')] = 1
) -> CategoryRead:
    """
    Return category with provided `id` with its `child`.

    Whether children will be obtained from a category depends on the `depth` parameter.
    Root categories have `depth` 0, their `child` have `depth` 1, and so on.
    If the `depth` for `child` of a certain category exceeds the passed `depth` parameter,
    then `child` of this category will not be received (`child` will be always an empty list)
    """
    async with uow:
        category = await uow.category.get_by_id(category_id)

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Category with id {category_id} does not exist')

        await refresh_sub_categories(uow, category, max_depth=depth)

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
async def create_category(uow: UOWDep, new_category: CategoryCreate) -> Category:
    """
    Create a new category. Categories can have the same names

    * Requires superuser privileges
    """
    async with uow:
        if new_category.parent_id is not None:
            parent_category = await uow.category.get_by_id(new_category.parent_id)
            if parent_category is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f'Category with id {new_category.parent_id} does not exist')

        new_category = Category(**new_category.model_dump())
        await uow.category.add(new_category)
        await uow.commit()

        await refresh_sub_categories(uow, new_category, max_depth=0)

    return new_category


@router.patch(
    '/{category_id}',
    dependencies=[Depends(current_user_id_admin)],
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
async def update_category(uow: UOWDep, category_id: int, category_update: CategoryUpdate) -> CategoryRead:
    """
    Update a category with provided `category_id`

    * Sub-categories depth is always 0, so child will be always empty list
    * Requires superuser privileges
    """
    async with uow:
        category = await uow.category.get_by_id(category_id)

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Category with id {category_id} does not exist')

        if category_update.parent_id is not None:
            parent_category = await uow.category.get_by_id(category_update.parent_id)
            if parent_category is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f'Category with id {category_update.parent_id} does not exist')

        update_data = category_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(category, field, value)

        await uow.category.update(category)
        await uow.commit()

        await refresh_sub_categories(uow, category, max_depth=0)  # Must be after commit!

    return category


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
async def delete_category(uow: UOWDep, category_id: int) -> None:
    """
    Delete category with provided `category_id`

    * Requires superuser privileges
    """
    async with uow:
        category = await uow.category.get_by_id(category_id)

        if category is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Category with id {category_id} does not exist')

        await uow.category.delete(category.id)
        await uow.commit()
