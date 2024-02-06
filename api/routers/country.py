from typing import Annotated

from fastapi import APIRouter, Query, HTTPException, status

from api.dependencies import UOWDep
from api.schemas.country import CountryRead


router = APIRouter(prefix='/country', tags=['Country'])


@router.get('/')
async def get_countries(
        uow: UOWDep,
        limit: Annotated[int, Query(ge=1, le=100)] = 100,
        offset: Annotated[int, Query(ge=0)] = 0
) -> list[CountryRead]:
    async with uow:
        countries = await uow.country.list(offset=offset, limit=limit)

    return countries


@router.get('/id/{country_id}')
async def get_country_by_id(country_id: int, uow: UOWDep) -> CountryRead:
    async with uow:
        country = await uow.country.get_by_id(country_id)
        if country is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Country with id {country_id} not found')

    return country


@router.get('/code/{country_code}')
async def get_country_by_code(country_code: str, uow: UOWDep) -> CountryRead:
    async with uow:
        country = await uow.country.get_by_code(country_code)
        if country is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f'Country with code {country_code} not found')

    return country
