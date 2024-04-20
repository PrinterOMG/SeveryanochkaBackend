import io
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from uuid import UUID

import aiofiles
from PIL import Image
from fastapi import UploadFile

from api.schemas.user import UserUpdate
from core.entities.user import UserEntity
from core.exceptions.user import BirthdayCanBeChangedOnceError, BadAvatarSizeError, BadAvatarTypeError, \
    BadAvatarResolutionError
from core.repositories.user import UserRepositoryBase
from core.unit_of_work import UnitOfWorkBase


class UserServiceBase(ABC):
    def __init__(
            self,
            user_repository: UserRepositoryBase,
            uow: UnitOfWorkBase,
    ):
        self._users_repository = user_repository
        self._uow = uow

    @abstractmethod
    async def create(self, phone: str, hashed_password: str) -> UserEntity:
        """

        :param phone:
        :param hashed_password:
        :raises UserAlreadyExistsError:
        :return:
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, current_user: UserEntity, update_data: UserUpdate) -> UserEntity:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_phone(self, phone: str) -> UserEntity | None:
        raise NotImplementedError

    @abstractmethod
    async def set_avatar(self, current_user: UserEntity, avatar: UploadFile) -> str:
        raise NotImplementedError

    @abstractmethod
    async def delete_avatar(self, current_user: UserEntity) -> None:
        raise NotImplementedError


class UserService(UserServiceBase):
    async def update(self, current_user: UserEntity, update_data: UserUpdate) -> UserEntity:
        if current_user.birthday is not None and current_user.birthday != update_data.birthday:
            raise BirthdayCanBeChangedOnceError

        current_user.birthday = update_data.birthday
        current_user.first_name = update_data.first_name
        current_user.last_name = update_data.last_name

        current_user = await self._users_repository.update(current_user)
        await self._uow.commit()
        return current_user

    async def create(self, phone: str, hashed_password: str) -> UserEntity:
        new_user = UserEntity(
            phone=phone,
            hashed_password=hashed_password,
            is_superuser=False
        )

        await self._users_repository.add(new_user)
        await self._uow.commit()

        return new_user

    async def get_by_id(self, user_id: UUID) -> UserEntity | None:
        return await self._users_repository.get_by_id(user_id)

    async def get_by_phone(self, phone: str) -> UserEntity | None:
        return await self._users_repository.get_by_phone(phone)

    async def set_avatar(self, current_user: UserEntity, avatar: UploadFile) -> str:
        if avatar.size > 10 * 1024 * 1024:
            raise BadAvatarSizeError

        if avatar.content_type not in ('image/jpeg', 'image/png'):
            raise BadAvatarTypeError

        file_bytes = io.BytesIO(await avatar.read())
        image = Image.open(file_bytes)
        width, height = image.size
        if width >= 1200 or height >= 1200:
            raise BadAvatarResolutionError

        output_directory = Path(f'static/users/{current_user.id}')
        output_directory.mkdir(exist_ok=True)

        extension = avatar.filename.split('.')[-1]
        random_str = str(uuid.uuid4()).replace('-', '')[:4]
        filename = f'avatar-{random_str}.{extension}'
        path_to_avatar = output_directory / filename

        async with aiofiles.open(path_to_avatar, mode='wb') as file:
            await file.write(file_bytes.getbuffer())

        old_avatar = current_user.avatar_url
        current_user.avatar_url = str(path_to_avatar)

        await self._users_repository.update(current_user)
        await self._uow.commit()

        if old_avatar is not None:
            Path(old_avatar).unlink(missing_ok=True)

        return current_user.avatar_url

    async def delete_avatar(self, current_user: UserEntity) -> None:
        if current_user.avatar_url is None:
            return

        avatar_path = current_user.avatar_url
        current_user.avatar_url = None
        await self._users_repository.update(current_user)
        await self._uow.commit()

        Path(avatar_path).unlink(missing_ok=True)
