from fastapi import HTTPException
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.database.postgres.models.base import Base


class BaseCrudMixin:
    async def __init__(
        self,
        model: Base,
        session: Session
    ):
        self.model = model
        self.session = session

    async def missing(self, obj, _id: int | None = None):
        if obj is None:
            raise HTTPException(
                detail=f"Object {_id} not found!",
                status_code=404
            )

    async def pagination(self, query, page: int = 1, page_size: int = 10):
        if page_size:
            query = query.limit(page_size)
        if (page-1):
            query = query.offset((page-1) * page_size)
        return query.all()

    async def pagination_query(self, query, page: int = 1, page_size: int = 10):
        if page_size:
            query = query.limit(page_size)
        if (page-1):
            query = query.offset((page-1) * page_size)
        return query
