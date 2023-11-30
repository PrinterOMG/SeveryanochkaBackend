from abc import ABC, abstractmethod

from database.base import async_session_maker
from database.repositories.customer import CustomerRepositoryBase, CustomerRepository


class UnitOfWorkBase(ABC):
    """
    Unit of work.
    """

    customers: CustomerRepositoryBase

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.rollback()

    @abstractmethod
    async def commit(self):
        """
        Commits the current transaction.
        """
        raise NotImplementedError()

    @abstractmethod
    async def rollback(self):
        """
        Rollbacks the current transaction.
        """
        raise NotImplementedError()


class UnitOfWork(UnitOfWorkBase):
    def __init__(self) -> None:
        """
        Creates a new uow instance.
        """
        self._session_factory = async_session_maker

    def __aenter__(self):
        self._session = self._session_factory()

        self.customers = CustomerRepository(self._session)

        return super().__aenter__()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
