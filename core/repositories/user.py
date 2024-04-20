from abc import abstractmethod, ABC

from sqlalchemy import select

from core.entities.user import UserEntity
from core.repositories.base import GenericRepository, GenericSARepository
from database.models.user import User


class UserRepositoryBase(GenericRepository[UserEntity], ABC):
    entity = UserEntity

    @abstractmethod
    async def get_by_phone(self, phone: str) -> UserEntity | None:
        raise NotImplementedError


class SAUserRepository(GenericSARepository, UserRepositoryBase):
    model_cls = User

    async def get_by_phone(self, phone: str) -> UserEntity | None:
        stmt = select(User).where(User.phone == phone)
        user = await self._session.scalar(stmt)
        if user is None:
            return None
        return self.entity.model_validate(user)
