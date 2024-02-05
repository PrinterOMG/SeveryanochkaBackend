from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker

from database.base import get_async_session_factory
from database.repositories.brand import BrandRepositoryBase, BrandRepository
from database.repositories.category import CategoryRepository, CategoryRepositoryBase
from database.repositories.phone_key import PhoneKeyRepositoryBase, PhoneKeyRepository
from database.repositories.user import UserRepositoryBase, UserRepository


class UnitOfWorkBase(ABC):
    """
    Unit of work.
    """

    users: UserRepositoryBase
    phone_key: PhoneKeyRepositoryBase
    category: CategoryRepositoryBase
    brand: BrandRepositoryBase

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
    def __init__(self, session_factory: Annotated[async_sessionmaker, Depends(get_async_session_factory)]) -> None:
        """
        Creates a new uow instance.
        """
        self._session_factory = session_factory

    def __aenter__(self):
        self._session = self._session_factory()

        self.users = UserRepository(self._session)
        self.phone_key = PhoneKeyRepository(self._session)
        self.category = CategoryRepository(self._session)
        self.brand = BrandRepository(self._session)

        return super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._session.expunge_all()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def refresh(self, instance, attribute_names: list[str] = None):
        await self._session.refresh(instance, attribute_names)

    async def expunge(self, obj):
        self._session.expunge(obj)
