from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query

from api.dependencies import current_user_id_admin, UOWDep
from api.schemas.brand import BrandRead, BrandCreate, BrandUpdate
from api.schemas.other import ErrorMessage
from database.models import Brand

router = APIRouter(prefix='/brands', tags=['BrandS'])


@router.get('')
async def get_brands(
        uow: UOWDep,
        limit: Annotated[int, Query(ge=1, le=20)] = 10,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[BrandRead]:
    async with uow:
        brands = await uow.brand.list(limit=limit, offset=offset)

    return brands


@router.get(
    '/{brand_id}',
    responses={
        404: {
            'model': ErrorMessage,
            'description': 'Brand not found'
        }
    }
)
async def get_brand(uow: UOWDep, brand_id: int) -> BrandRead:
    async with uow:
        brand = await uow.brand.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Brand with id {brand_id} not found')

    return brand


@router.post(
    '',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_201_CREATED,
    response_model=BrandRead
)
async def create_brand(uow: UOWDep, new_brand: BrandCreate) -> Brand:
    async with uow:
        brand = Brand(**new_brand.model_dump())
        brand = await uow.brand.add(brand)

        await uow.commit()

    return brand


@router.patch(
    '/{brand_id}',
    dependencies=[Depends(current_user_id_admin)],
    responses={
        404: {
            'model': ErrorMessage,
            'description': 'Brand not found'
        }
    }
)
async def update_brand(brand_id: int, uow: UOWDep, brand_update: BrandUpdate) -> BrandRead:
    async with uow:
        brand = await uow.brand.get_by_id(brand_id)

        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Brand with id {brand_id} not found')

        update_data = brand_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(brand, field, value)

        await uow.brand.update(brand)
        await uow.commit()

    return brand


@router.delete(
    '/{brand_id}',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            'model': ErrorMessage,
            'description': 'Brand not found'
        }
    }
)
async def delete_brand(brand_id: int, uow: UOWDep) -> None:
    async with uow:
        brand = await uow.brand.get_by_id(brand_id)

        if brand is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Brand with id {brand_id} not found')

        await uow.brand.delete(brand_id)
        await uow.commit()
