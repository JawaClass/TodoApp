from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, Select
from fastapi import Query
from pydantic import BaseModel
from math import ceil


class PaginationParams(BaseModel):
    page: int
    size: int


class PaginationMeta(BaseModel):
    total: int
    page: int
    size: int
    pages: int


class Page[E](BaseModel):
    meta: PaginationMeta
    items: list[E]


def get_pagination_params(
    page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)
) -> PaginationParams:
    return PaginationParams(page=page, size=size)


async def paginate_query(stmt: Select, session: AsyncSession, params: PaginationParams):
    # Count total records
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await session.execute(count_stmt)).scalar()

    # Apply limit/offset
    offset = (params.page - 1) * params.size
    paginated_stmt = stmt.offset(offset).limit(params.size)
    items = (await session.execute(paginated_stmt)).scalars().all()

    meta = PaginationMeta(
        total=total,
        page=params.page,
        size=params.size,
        pages=ceil(total / params.size) if params.size else 1,
    )
    return Page(meta=meta, items=items)
