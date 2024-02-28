from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = 'postgres'
    postgres_port: int = 5432

    database_url: str = ''

    test_database_url: str = ''
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expires_minutes: int = 30

    def __init__(self):
        super().__init__()
        self.database_url = f'postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'

    class Config:
        env_prefix = ''
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
