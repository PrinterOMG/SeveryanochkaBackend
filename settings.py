from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(env='DATABASE_URL')
    test_database_url: str = ''
    secret_key: str = Field(env='SECRET_KEY')
    algorithm: str = Field(env='ALGORITHM', default='HS256')
    access_token_expires_minutes: int = Field(env='ACCESS_TOKEN_EXPIRES_MINUTES', default=30)

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
