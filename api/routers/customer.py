from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from api.dependencies import UOWDep
from api.schemas.customer import CustomerOut
from api.schemas.other import Message

customer_router = APIRouter(prefix='/customer', tags=['Customer'])


@customer_router.get(
    '/{id}',
    response_model=CustomerOut,
    responses={
        404: {
            'model': Message
        }
    }
)
async def get_customer(uow: UOWDep, customer_id: int):
    async with uow:
        customer = await uow.customers.get_by_id(customer_id)

        return customer.to_dict() if customer else JSONResponse(status_code=404,content={'message': 'Customer not found'})
