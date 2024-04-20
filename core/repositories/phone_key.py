from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from sqlalchemy import select, update

from core.entities.phone_key import PhoneKeyEntity
from core.exceptions.base import EntityNotFoundError
from core.repositories.base import GenericRepository, GenericSARepository
from database.models import PhoneKey


class PhoneKeyRepositoryBase(GenericRepository[PhoneKeyEntity], ABC):
    entity = PhoneKeyEntity

    @abstractmethod
    async def get_by_key(self, key: str) -> PhoneKeyEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKeyEntity]:
        raise NotImplementedError

    @abstractmethod
    async def mark_as_used_by_key(self, key: str) -> PhoneKeyEntity:
        raise NotImplementedError


class SAPhoneKeyRepository(GenericSARepository, PhoneKeyRepositoryBase):
    model_cls = PhoneKey

    async def get_by_key(self, key: str) -> PhoneKeyEntity | None:
        stmt = select(PhoneKey).where(PhoneKey.key == key)
        record = await self._session.scalar(stmt)

        if record is None:
            return None
        return PhoneKeyEntity.model_validate(record)

    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKeyEntity]:
        hour_ago_date = datetime.utcnow() - timedelta(hours=1)
        stmt = select(PhoneKey).where(PhoneKey.phone == phone, PhoneKey.created_at > hour_ago_date)
        records = await self._session.scalars(stmt)

        return [PhoneKeyEntity.model_validate(record) for record in records]

    async def mark_as_used_by_key(self, key: str) -> PhoneKeyEntity:
        stmt = (
            update(PhoneKey)
            .where(PhoneKey.key == key)
            .values(
                is_used=True,
                used_at=datetime.utcnow()
            )
            .returning(PhoneKey)
        )

        record = await self._session.scalar(stmt)
        if record is None:
            raise EntityNotFoundError(entity=PhoneKeyEntity, find_query=key)

        return PhoneKeyEntity.model_validate(record)
