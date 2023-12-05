from abc import abstractmethod, ABC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user import User
from database.repositories.base import GenericRepository, GenericSqlRepository


class UserRepositoryBase(GenericRepository[User], ABC):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None:
        raise NotImplementedError()


class UserRepository(GenericSqlRepository[User], UserRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_phone(self, phone: str) -> User | None:
        stmt = select(User).where(User.phone == phone)
        record = await self._session.execute(stmt)
        return record.scalar_one_or_none()
