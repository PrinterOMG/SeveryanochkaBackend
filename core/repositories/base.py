from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, and_, Select, update, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.base import EntityNotFoundError, EntityAlreadyExistsError
from database.base import Base

T = TypeVar('T', bound=BaseModel)


class GenericRepository(Generic[T], ABC):
    entity: Type[T]

    @abstractmethod
    async def get_by_id(self, id: UUID) -> T | None:
        """
        Get a single record by id

        :param id: Record id
        :return: Record or None
        """
        raise NotImplementedError()

    @abstractmethod
    async def list(self, offset: int = 0, limit: int = 100, **filters) -> list[T]:
        """
        Get a list of records

        :param limit:
        :param offset:
        :param filters: Filter conditions, several criteria are linked with a logical 'and'
        :raise ValueError: Invalid filter condition
        :return: List of records
        """
        raise NotImplementedError()

    @abstractmethod
    async def add(self, entity: T) -> T:
        """
        Creates a new record

        :param entity: The record to be created
        :return: The created record
        """
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: T, **kwargs) -> T:
        """
        Updates an existing record.
        Searches for the record needed to update by the id attribute in the transferred record

        :param entity: The record to be updated including record id
        :return: The updated record
        """
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """
        Deletes a record by id

        :param id: Record id
        :return: None
        """
        raise NotImplementedError()


class GenericSARepository(GenericRepository[T], ABC):
    model_cls: Type[Base]

    def __init__(self, session: AsyncSession) -> None:
        """
        Creates a new repository instance

        :param session: SQLAlchemy async session
        """
        self._session = session

    async def _convert_to_entity(self, record: Base, **kwargs) -> T:
        return self.entity.model_validate(record)

    def _construct_get_stmt(self, id: UUID) -> Select:
        """
        Creates a SELECT query for retrieving a single record

        :param id: Record id
        :return: SELECT statement
        """
        stmt = select(self.model_cls).where(self.model_cls.id == id)

        return stmt

    def _construct_list_stmt(self, offset, limit, **filters) -> Select:
        """
        Creates a SELECT query for retrieving a multiple records

        :param offset:
        :param limit:
        :param filters: Filter conditions, several criteria are linked with a logical 'and'
        :return: SELECT statement
        """
        stmt = select(self.model_cls)
        where_clauses = []
        for column, value in filters.items():
            if not hasattr(self.model_cls, column):
                raise ValueError(f'Invalid column name {column}')
            where_clauses.append(getattr(self.model_cls, column) == value)

        if len(where_clauses) == 1:
            stmt = stmt.where(where_clauses[0])
        elif len(where_clauses) > 1:
            stmt = stmt.where(and_(*where_clauses))

        stmt = stmt.offset(offset).limit(limit)

        return stmt

    async def get_by_id(self, id: UUID) -> T | None:
        stmt = self._construct_get_stmt(id)
        result = await self._session.scalar(stmt)

        if result is None:
            return None

        return await self._convert_to_entity(result)

    async def list(self, offset=0, limit=100, **filters) -> list[T]:
        stmt = self._construct_list_stmt(offset=offset, limit=limit, **filters)
        records = await self._session.scalars(stmt)

        return [await self._convert_to_entity(record) for record in records.all()]

    async def add(self, entity: T) -> T:
        record = self.model_cls(**entity.model_dump())

        self._session.add(record)

        try:
            await self._session.flush()
        except IntegrityError as error:
            raise EntityAlreadyExistsError(entity=self.entity) from error

        await self._session.refresh(record)

        return await self._convert_to_entity(record)

    async def update(self, entity: T, **kwargs) -> T:
        stmt = (
            update(self.model_cls)
            .where(self.model_cls.id == entity.id)
            .values(**entity.model_dump(exclude={'id'}))
            .returning(self.model_cls)
        )

        record = await self._session.scalar(stmt)
        if record is None:
            raise EntityNotFoundError(entity=self.entity, find_query=entity.id)

        return await self._convert_to_entity(record)

    async def delete(self, id: UUID) -> None:
        stmt = (
            delete(self.model_cls)
            .where(self.model_cls.id == id)
        )

        await self._session.execute(stmt)
