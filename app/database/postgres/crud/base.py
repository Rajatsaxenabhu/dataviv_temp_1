import sqlalchemy as sa
from sqlalchemy.orm import Session
from typing import List
from fastapi.exceptions import HTTPException

from app.database.postgres.deps import PostgresDB

from .crud_mixins import BaseCrudMixin
from app.conf.metaclass import Singleton
from ..models.base import BaseModel


class BaseCrud(BaseCrudMixin, metaclass=Singleton):
    def __init__(
        self,
        model: BaseModel,
        session: Session = PostgresDB().session()
    ):
        self.model = model
        self.session = session

    async def get_by_token(
        self,
        token: str
    ):

        obj = self.session.query(self.model).filter(
            self.model.token == token
        ).first()
        await self.missing(obj, token)
        return obj

    async def get_all(
        self,
        page: int = 0,
        page_size: int = 10
    ) -> List[BaseModel]:

        query = self.session.query(
            self.model
        ).filter().order_by(
            sa.desc(
                self.model.updated_at
            )
        )
        return await self.pagination(query, page, page_size)

    async def create(
        self,
        data: dict
    ) -> BaseModel:

        obj = self.model(**data)
        self.session.add(obj)
        self.session.commit()
        return obj

    async def create_many(self, data_list) -> None:
        obj_list = [self.model(**data) for data in data_list]
        obj = self.session.add_all(obj_list)
        self.session.commit()
        return obj

    async def get(self, _id: int) -> BaseModel:
        obj = self.session.query(
            self.model
        ).filter(
            self.model.id == _id
        ).first()
        await self.missing(obj, _id)
        return obj

    async def delete_obj(self, obj) -> None:
        await self.missing(obj)
        self.session.delete(obj)
        self.session.commit()

    async def delete(self, _id: int) -> None:

        obj = self.session.query(
            self.model
        ).filter(
            self.model.id == _id
        ).first()
        await self.missing(obj, _id)
        return await self.delete_obj(obj)

    async def update_obj(self, obj, data: dict) -> BaseModel:
        await self.missing(obj)
        for key, value in data.items():
            setattr(obj, key, value)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    async def update(self, _id: int, data: dict) -> BaseModel:
        obj = self.session.query(self.model).filter(
            self.model.id == _id).first()
        await self.missing(obj, _id)
        return await self.update_obj(obj, data)

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 20
    ):

        query = sa.select(
            self.model
        ).select_from(
            self.model
        ).where(
            self.model.c.title.match(query)
        ).order_by(
            sa.desc(
                self.model.updated_at
            )
        )
        query = self.pagination_query(query, page, page_size)
        return self.session.execute(query).scalars.all()

    async def vector_search(self, query: str, page: int = 0, page_size: int = 30):
        results = self.session.query(self.model).filter(
            self.model.search_vector.match(query))
        return await self.pagination(results, page, page_size)
