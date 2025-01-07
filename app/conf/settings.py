from typing import List
from pydantic_settings import BaseSettings
from pydantic import EmailStr, Field,  AnyHttpUrl
from decouple import config
from datetime import datetime, timezone
from dotenv import load_dotenv
import pytz
import sqlalchemy as sa

load_dotenv()

asia_timezone = pytz.timezone('Asia/Kolkata')


def current_datetime() -> datetime:
    return datetime.now(asia_timezone)


SQL_DATABASE_CONF: dict = {
    "username": config("POSTGRES_USER"),
    "password": config("POSTGRES_PASSWORD"),
    "host": config("POSTGRES_HOST"),
    "port": config("POSTGRES_PORT"),
    "database": config("POSTGRES_DB"),
}


class Settings(BaseSettings):
    SECRET_KEY: str

    ENV: str
    DEBUG: bool

    CLIENT_ORIGIN: str
    ALLOWED_ORIGIN: List[str] = config('CLIENT_ORIGIN', cast=str).split(",")

    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_POOL_SIZE: int = 1
    POSTGRES_MAX_POOL: int = 2
    POSTGRES_ENGINE_ECHO: bool = False

    SQLALCHEMY_DATABASE_URL_LOCAL: AnyHttpUrl = Field(
        "sqlite:///db.sqlite", validate_default=False)

    SQLALCHEMY_DATABASE_URL_DEV: AnyHttpUrl = Field(
        sa.URL.create(
            drivername="postgresql+psycopg2",
            **SQL_DATABASE_CONF
        ), validate_default=False
    )
    SQLALCHEMY_DATABASE_URL_PROD: AnyHttpUrl = Field(
        sa.URL.create(
            drivername="postgresql+psycopg2",
            **SQL_DATABASE_CONF
        ),
        validate_default=False
    )

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    REDIS_BROKER_URL: str = Field(
        config('REDIS_BROKER_URL', cast=str, default="redis://localhost:6379/0"))
    REDIS_BACKEND_URL: str = Field(
        config('REDIS_BACKEND_URL', cast=str, default="redis://localhost:6379/0"))

    SQL_CELERY_RESULT_BACKEND_URL: AnyHttpUrl = Field(
        sa.URL.create(
            drivername="db+postgresql",
            **SQL_DATABASE_CONF
        ),
        validate_default=False
    )

    class Config:
        env_file = '.env'


settings = Settings()
