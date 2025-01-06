from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pydantic_settings import BaseSettings
from .db_schema import Base


class Settings(BaseSettings):
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    REDIS_PORT: str
    POSTGRES_TASK_DB: str

    @property
    def REDIS_ADDRESS(self) -> str:
        return f'redis://localhost:{self.REDIS_PORT}'

    @property
    def DB_ADDRESS(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_TASK_DB}'

    class Config:
        env_file = ".env"  



settings_obj = Settings()


engine = create_engine(settings_obj.DB_ADDRESS)

if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(bind=engine)

print(f"Database exists: {database_exists(engine.url)}")


SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
