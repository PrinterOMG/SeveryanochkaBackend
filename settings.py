from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    test_database_url: str = ''
    secret_key: str
    algorithm: str = 'HS256'
    access_token_expires_minutes: int = 30

    class Config:
        env_prefix = ''
        case_sensitive = False
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
