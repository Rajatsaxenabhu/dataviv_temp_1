from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    REDIS_PORT: str

    @property
    def REDIS_ADDRESS(self)->str:
        return f'redis://localhost:{self.REDIS_PORT}'

    @property
    def DB_ADDRESS(self)->str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
    class Config:
        env_file = ".env"  # Path to the .env file

settings_obj = Settings()
engine=create_engine(settings_obj.DB_ADDRESS)
session=sessionmaker(bind=engine)
def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()