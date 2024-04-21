from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, HTTPException, status

from api.dependencies import CountryServiceDep
from api.schemas.country import CountryRead


router = APIRouter(prefix='/countries', tags=['Countries'])


@router.get('/', response_model=list[CountryRead])
async def get_countries(
    country_service: CountryServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await country_service.get_all(limit=limit, offset=offset)


@router.get('/id/{country_id}', response_model=CountryRead)
async def get_country_by_id(country_id: UUID, country_service: CountryServiceDep):
    country = await country_service.get_by_id(country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Country with id {country_id} not found',
        )

    return country


@router.get('/code/{country_code}', response_model=CountryRead)
async def get_country_by_code(country_code: str, country_service: CountryServiceDep):
    country = await country_service.get_by_code(country_code)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Country with code {country_code} not found',
        )

    return country
