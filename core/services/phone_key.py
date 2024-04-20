import uuid
from abc import abstractmethod, ABC
from datetime import datetime, timedelta

from core.entities.phone_key import PhoneKeyEntity
from core.exceptions.phone_key import PhoneKeyCreateLimitError, BadPhoneKeyError, BadConfirmationCodeError
from core.repositories.phone_key import PhoneKeyRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class PhoneKeyServiceBase(ABC):
    def __init__(
            self,
            phone_key_repository: PhoneKeyRepositoryBase,
            uow: UnitOfWorkBase,
    ):
        self.phone_key_repository = phone_key_repository
        self.uow = uow

    @abstractmethod
    async def get_by_key(self, key: str) -> PhoneKeyEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_ready_to_use_by_key(self, key: str) -> PhoneKeyEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKeyEntity]:
        raise NotImplementedError

    @abstractmethod
    async def use_by_key(self, key: str) -> PhoneKeyEntity:
        raise NotImplementedError

    @abstractmethod
    async def create(self, phone: str) -> PhoneKeyEntity:
        """
        :param phone:
        :raises PhoneKeyCreateLimitError:
        :return: PhoneKeyEntity
        """
        raise NotImplementedError

    @abstractmethod
    async def verify(self, key: str, code: str) -> PhoneKeyEntity:
        raise NotImplementedError


class PhoneKeyService(PhoneKeyServiceBase):
    async def get_by_key(self, key: str) -> PhoneKeyEntity:
        return await self.phone_key_repository.get_by_key(key)

    async def get_ready_to_use_by_key(self, key: str) -> PhoneKeyEntity:
        phone_key = await self.phone_key_repository.get_by_key(key)

        if phone_key is None or not phone_key.is_ready_to_use:
            raise BadPhoneKeyError

        return phone_key

    async def use_by_key(self, key: str) -> PhoneKeyEntity:
        phone_key = await self.phone_key_repository.mark_as_used_by_key(key)
        await self.uow.commit()
        return phone_key

    async def get_last_hour_keys_by_phone(self, phone: str) -> list[PhoneKeyEntity]:
        return await self.phone_key_repository.get_last_hour_keys_by_phone(phone)

    async def create(self, phone: str) -> PhoneKeyEntity:
        phone_keys = await self.get_last_hour_keys_by_phone(phone)
        if len(phone_keys) >= 3:
            raise PhoneKeyCreateLimitError

        key = str(uuid.uuid4())  # Получение ключа от стороннего сервиса
        expire_date = datetime.utcnow() + timedelta(minutes=15)
        phone_key = PhoneKeyEntity(
            key=key,
            phone=phone,
            expires_at=expire_date
        )
        await self.phone_key_repository.add(phone_key)
        await self.uow.commit()

        return phone_key

    async def verify(self, key: str, code: str) -> PhoneKeyEntity:
        phone_key = await self.phone_key_repository.get_by_key(key)

        if phone_key is None or phone_key.expires_at < datetime.utcnow() or phone_key.is_verified:
            raise BadPhoneKeyError

        is_correct_code = code == '0000'  # Проверка кода через сторонний сервис
        if not is_correct_code:
            raise BadConfirmationCodeError(code)

        phone_key.is_verified = True
        phone_key.verified_at = datetime.utcnow()
        phone_key.expires_at = datetime.utcnow() + timedelta(minutes=10)
        phone_key = await self.phone_key_repository.update(phone_key)
        await self.uow.commit()

        return phone_key
