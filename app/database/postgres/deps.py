from typing import Annotated
from .sessions import SessionLocal
from fastapi import Depends

from sqlalchemy.orm import Session


class PostgresDb():
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                PostgresDb, cls).__new__(cls, *args, **kwargs)
            cls._instances[cls]._session = SessionLocal()
        return cls._instances[cls]

    def session(self) -> Session:
        return self._session

    def get_new_session(self) -> Session:
        return SessionLocal()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pg_session_dependency = Annotated[Session, Depends(PostgresDb().session)]

class PostgresDbContext:
    def __init__(self):
        self.db = PostgresDb().get_new_session()
    
    def __enter__(self):
        return self.db
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()