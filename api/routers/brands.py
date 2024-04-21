from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, status, HTTPException, Query, Depends

from api.dependencies import current_user_id_admin, BrandsServiceDep
from api.schemas.brand import BrandRead, BrandCreate, BrandUpdate
from api.schemas.other import ErrorMessage
from core.exceptions.base import EntityNotFoundError

router = APIRouter(prefix='/brands', tags=['Brands'])


@router.get('', response_model=list[BrandRead])
async def get_brands(
    brand_service: BrandsServiceDep,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await brand_service.get_all(limit=limit, offset=offset)


@router.get(
    '/{brand_id}',
    responses={404: {'model': ErrorMessage, 'description': 'Brand not found'}},
    response_model=BrandRead,
)
async def get_brand(brand_service: BrandsServiceDep, brand_id: UUID):
    brand = await brand_service.get_by_id(brand_id)

    if brand is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Brand with id {brand_id} not found',
        )

    return brand


@router.post(
    '',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_201_CREATED,
    response_model=BrandRead,
)
async def create_brand(brand_service: BrandsServiceDep, new_brand: BrandCreate):
    return await brand_service.create(new_brand)


@router.put(
    '/{brand_id}',
    dependencies=[Depends(current_user_id_admin)],
    response_model=BrandRead,
    responses={404: {'model': ErrorMessage, 'description': 'Brand not found'}},
)
async def update_brand(
    brand_id: UUID, brand_update: BrandUpdate, brand_service: BrandsServiceDep
):
    try:
        brand = await brand_service.update(brand_id, brand_update)
    except EntityNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(error)
        ) from error

    return brand


@router.delete(
    '/{brand_id}',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {'model': ErrorMessage, 'description': 'Brand not found'}},
)
async def delete_brand(brand_id: UUID, brand_service: BrandsServiceDep) -> None:
    await brand_service.delete(brand_id)
