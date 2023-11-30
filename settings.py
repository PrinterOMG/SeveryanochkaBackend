from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_connection_str: str = Field(env='DATABASE_URL')

    class Config:
        env_prefix = ""
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
