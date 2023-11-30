from typing import Annotated

from fastapi import Depends

from services.unit_of_work import UnitOfWorkBase, UnitOfWork

UOWDep = Annotated[UnitOfWorkBase, Depends(UnitOfWork)]
