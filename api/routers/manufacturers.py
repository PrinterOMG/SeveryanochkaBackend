from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Depends, HTTPException, status

from api.dependencies import ManufacturerServiceDep, current_user_id_admin
from api.schemas.manufacturer import ManufacturerRead, ManufacturerCreate, ManufacturerUpdate
from core.exceptions.base import EntityNotFoundError

router = APIRouter(prefix='/test_manufacturers', tags=['Manufacturers'])


@router.get('', response_model=list[ManufacturerRead])
async def get_manufacturers(
        manufacturer_service: ManufacturerServiceDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0
):
    return await manufacturer_service.get_all(limit=limit, offset=offset)


@router.get('/{manufacturer_id}', response_model=ManufacturerRead)
async def get_manufacturer(manufacturer_service: ManufacturerServiceDep, manufacturer_id: UUID):
    manufacturer = await manufacturer_service.get_by_id(manufacturer_id)

    if manufacturer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Manufacturer with id {manufacturer_id} not found'
        )

    return manufacturer


@router.post(
    '',
    dependencies=[Depends(current_user_id_admin)],
    response_model=ManufacturerRead,
    status_code=201
)
async def create_manufacturer(
        manufacturer_service: ManufacturerServiceDep,
        new_manufacturer: ManufacturerCreate
):
    return await manufacturer_service.create(new_manufacturer)


@router.put(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)]
)
async def update_manufacturer(
        manufacturer_service: ManufacturerServiceDep,
        manufacturer_id: UUID,
        manufacturer_update: ManufacturerUpdate
) -> ManufacturerRead:
    try:
        return await manufacturer_service.update(manufacturer_id, manufacturer_update)
    except EntityNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Manufacturer with id {manufacturer_id} does not exist'
        )


@router.delete(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_manufacturer(manufacturer_service: ManufacturerServiceDep, manufacturer_id: UUID):
    await manufacturer_service.delete(manufacturer_id)
