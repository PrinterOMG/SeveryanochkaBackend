from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa

from settings import settings

engine = create_async_engine(settings.database_connection_str)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(sa.BigInteger, primary_key=True, autoincrement=True)

    def to_dict(self) -> dict:
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}


async def get_async_session_factory() -> async_sessionmaker:
    return async_session_maker
