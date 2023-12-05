from abc import ABC, abstractmethod

from database.base import async_session_maker
from database.repositories.phone_key import PhoneKeyRepositoryBase, PhoneKeyRepository
from database.repositories.user import UserRepositoryBase, UserRepository


class UnitOfWorkBase(ABC):
    """
    Unit of work.
    """

    users: UserRepositoryBase
    phone_key: PhoneKeyRepositoryBase

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

        self.users = UserRepository(self._session)
        self.phone_key = PhoneKeyRepository(self._session)

        return super().__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._session.expunge_all()
        await super().__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()

    async def expunge(self, obj):
        self._session.expunge(obj)
