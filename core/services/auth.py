from abc import abstractmethod, ABC
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from api.schemas.auth import RegisterRequest, TokenRead, ResetPasswordRequest
from config import Settings
from core.entities.auth import Token
from core.exceptions.auth import BadCredentialsError
from core.repositories.user import UserRepositoryBase
from core.security import create_access_token, get_password_hash, verify_password
from core.services.phone_key import PhoneKeyServiceBase
from core.services.user import UserServiceBase
from core.unit_of_work import UnitOfWorkBase


class AuthServiceBase(ABC):
    def __init__(
            self,
            user_service: UserServiceBase,
            phone_key_service: PhoneKeyServiceBase,
            settings: Settings
    ):
        self._user_service = user_service
        self._phone_key_service = phone_key_service
        self._settings = settings

    @abstractmethod
    async def register_user(self, register_data: RegisterRequest) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def login_user(self, login_data: OAuth2PasswordRequestForm) -> Token:
        raise NotImplementedError

    @abstractmethod
    async def reset_password(self, reset_data: ResetPasswordRequest) -> None:
        raise NotImplementedError


class AuthService(AuthServiceBase):
    def _create_token(self, user_id):
        access_token_expires = timedelta(minutes=self._settings.access_token_expires_minutes)
        access_token = create_access_token(
            data={'sub': str(user_id)}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token)

    async def register_user(self, register_data: RegisterRequest) -> Token:
        phone_key = await self._phone_key_service.get_ready_to_use_by_key(register_data.phone_key)

        new_user = await self._user_service.create(
            phone=phone_key.phone,
            hashed_password=get_password_hash(register_data.password)
        )

        await self._phone_key_service.use_by_key(phone_key.key)

        return self._create_token(new_user.id)

    async def login_user(self, login_data: OAuth2PasswordRequestForm) -> Token:
        user = await self._user_service.get_by_phone(login_data.username)

        if user is None or not verify_password(login_data.password, user.hashed_password):
            raise BadCredentialsError

        return self._create_token(user.id)

    async def reset_password(self, reset_data: ResetPasswordRequest) -> None:
        phone_key = await self._phone_key_service.get_ready_to_use_by_key(reset_data.phone_key)

        user = await self._user_service.get_by_phone(phone_key.phone)
        user.hashed_password = get_password_hash(reset_data.password)

        await self._user_service.update(user)
        await self._phone_key_service.use_by_key(phone_key.key)

