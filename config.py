from functools import lru_cache, cached_property

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = 'postgres'
    postgres_port: int = 5432

    secret_key: str
    algorithm: str = 'HS256'
    access_token_expires_minutes: int = 30

    @cached_property
    def database_url(self) -> str:
        return (f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@'
                f'{self.postgres_host}:{self.postgres_port}/{self.postgres_db}')

    class Config:
        env_prefix = ''
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'
        frozen = True


@lru_cache
def get_settings():
    return Settings()
