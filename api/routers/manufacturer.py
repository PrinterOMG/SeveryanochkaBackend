from typing import Annotated

from fastapi import APIRouter, Query, Depends, HTTPException, status

from api.dependencies import UOWDep, current_user_id_admin
from api.schemas.manufacturer import ManufacturerRead, ManufacturerCreate, ManufacturerUpdate
from database.models import Manufacturer

router = APIRouter(prefix='/manufacturer', tags=['Manufacturer'])


@router.get('')
async def get_manufacturers(
        uow: UOWDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[ManufacturerRead]:
    async with uow:
        manufacturers = await uow.manufacturer.list(limit=limit, offset=offset)

    return manufacturers


@router.get('/{manufacturer_id}')
async def get_manufacturer(uow: UOWDep, manufacturer_id: int) -> ManufacturerRead:
    async with uow:
        manufacturer = await uow.manufacturer.get_by_id(manufacturer_id)

        if manufacturer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Manufacturer with id {manufacturer_id} not found')

    return manufacturer


@router.post(
    '',
    dependencies=[Depends(current_user_id_admin)],
    response_model=ManufacturerRead,
    status_code=201
)
async def create_manufacturer(uow: UOWDep, new_manufacturer: ManufacturerCreate) -> Manufacturer:
    async with uow:
        manufacturer = Manufacturer(**new_manufacturer.model_dump())

        await uow.manufacturer.add(manufacturer)
        await uow.commit()
    return manufacturer


@router.patch(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)]
)
async def update_manufacturer(
        uow: UOWDep,
        manufacturer_id: int,
        manufacturer_update: ManufacturerUpdate
) -> ManufacturerRead:
    async with uow:
        manufacturer = await uow.manufacturer.get_by_id(manufacturer_id)

        if manufacturer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Manufacturer with id {manufacturer_id} does not exist')

        update_data = manufacturer_update.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(manufacturer, field, value)

        await uow.manufacturer.update(manufacturer)
        await uow.commit()

    return manufacturer


@router.delete(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)],
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_manufacturer(uow: UOWDep, manufacturer_id: int):
    async with uow:
        manufacturer = await uow.manufacturer.get_by_id(manufacturer_id)

        if manufacturer is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Manufacturer with id {manufacturer_id} not found')

        await uow.manufacturer.delete(manufacturer_id)
        await uow.commit()
