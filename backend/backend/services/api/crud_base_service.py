from typing import Any, Generic, TypeVar
from backend.models.model import SqlAlchemyBase
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from pydantic import BaseModel
from backend.routes.util.pagination import PaginationParams, paginate_query
from backend.sa_util.relationships import select_relationships_deep

T = TypeVar("T", bound=SqlAlchemyBase)


class CrudUtilMixin(Generic[T]):
    db: AsyncSession

    async def save_entity(self, entity: T) -> T:
        self.db.add(entity)
        await self.db.commit()
        await self.db.refresh(entity)
        return entity

    async def delete_entity(self, entity: T) -> T:
        await self.db.delete(entity)
        await self.db.commit()
        return entity


class CrudBaseService(CrudUtilMixin[T], Generic[T]):
    def __init__(
        self,
        sa_type_: type[T],
        db: AsyncSession,
        pk_name: str = "id",
        mask_class: BaseModel = None,
    ):
        self.sa_type_ = sa_type_
        self.db = db
        self.pk_name = pk_name
        self.mask_class = mask_class

    async def get_all(self, params: PaginationParams, /, where_clause: Any = None):
        stmt = sa.select(self.sa_type_)
        if where_clause:
            stmt = stmt.where(where_clause)
        return await paginate_query(stmt, self.db, params)

    async def get_by_id(self, id: int, mask_class: BaseModel = None) -> T | None:
        mask_class = self.mask_class or mask_class
        if mask_class:
            stmt = sa.select(self.sa_type_).where(
                getattr(self.sa_type_, self.pk_name) == id
            )
            loads = select_relationships_deep(self.sa_type_, mask_class)
            stmt = stmt.options(*loads)
            item = (await self.db.execute(stmt)).scalar()
        else:
            item = await self.db.get(self.sa_type_, id)
        return item

    async def delete_by_id(self, id: int):
        entity = await self.get_by_id(id)
        return await self.delete(entity)

    async def delete(self, entity: T):
        return await self.delete_entity(entity)

    async def add(self, model: BaseModel):
        item = self.sa_type_(**model.model_dump())
        return await self.save_entity(item)

    async def update(
        self,
        update_model: BaseModel,
        /,
        id: int = None,
        entity: T = None,
        patch: bool = True,
    ):
        values = update_model.model_dump(exclude_unset=patch)
        entity = await self._entity(entity, id)
        for name, value in values.items():
            setattr(entity, name, value)

        result = await self.save_entity(entity)
        return result

    async def _entity(self, entity: T | None = None, id: int | None = None) -> T:
        if entity is not None:
            return entity

        if id is None:
            raise ValueError("Either 'entity' or 'id' must be provided.")

        entity = await self.get_by_id(id)
        if entity is None:
            raise ValueError(f"{self.sa_type_.__name__} with ID {id} not found.")

        return entity
