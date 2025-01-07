from typing import Annotated
from .sessions import SessionLocal
from fastapi import Depends

from sqlalchemy.orm import Session


class PostgresDB():
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                PostgresDB, cls).__new__(cls, *args, **kwargs)
            cls._instances[cls]._session = SessionLocal()
        return cls._instances[cls]

    def session(self) -> Session:
        return self._session


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


pg_session_dependency = Annotated[Session, Depends(PostgresDB().session)]
