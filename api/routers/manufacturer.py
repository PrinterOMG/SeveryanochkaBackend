from typing import Annotated

from fastapi import APIRouter, Query, Depends

from api.dependencies import UOWDep, current_user_id_admin
from api.schemas.manufacturer import ManufacturerRead

router = APIRouter(prefix='/manufacturer', tags=['Manufacturer'])


@router.get('')
async def get_manufacturers(
        uow: UOWDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[ManufacturerRead]:
    pass


@router.get('/{manufacturer_id}')
async def get_manufacturer(uow: UOWDep):
    pass


@router.post(
    '',
    dependencies=[Depends(current_user_id_admin)]
)
async def create_manufacturer(uow: UOWDep):
    pass


@router.patch(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)]
)
async def update_manufacturer(uow: UOWDep):
    pass


@router.delete(
    '/{manufacturer_id}',
    dependencies=[Depends(current_user_id_admin)]
)
async def delete_manufacturer(uow: UOWDep):
    pass
