from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import PhoneKey
from database.repositories.base import GenericRepository, GenericSqlRepository


class PhoneKeyRepositoryBase(GenericRepository[PhoneKey], ABC):
    @abstractmethod
    async def get_by_key(self, key: str) -> PhoneKey | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKey]:
        raise NotImplementedError()


class PhoneKeyRepository(GenericSqlRepository[PhoneKey], PhoneKeyRepositoryBase):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, PhoneKey)

    async def get_by_key(self, key: str) -> PhoneKey | None:
        stmt = select(PhoneKey).where(PhoneKey.key == key)
        record = await self._session.execute(stmt)
        return record.scalar_one_or_none()

    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKey]:
        hour_ago_date = datetime.utcnow() - timedelta(hours=1)
        stmt = select(PhoneKey).where(PhoneKey.phone == phone, PhoneKey.created_at > hour_ago_date)
        records = await self._session.execute(stmt)
        return records.scalars().all()
