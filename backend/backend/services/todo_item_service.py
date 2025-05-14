from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.routes.util.pagination import Page, PaginationParams, paginate_query
from backend.models import model
from backend.models.api import TodoItemIn

async def get_all_for_user(
    user: model.User,
    session: AsyncSession,
    params: PaginationParams
):
    stmt = (
        select(model.TodoItem)
        .where(model.TodoItem.creator_id == user.id)
        .order_by(model.TodoItem.create_date.desc())
    )
    return await paginate_query(stmt, session, params)
    

async def add_new_item(item_in: TodoItemIn, user_id: int, session: AsyncSession):

    item = model.TodoItem(**item_in.model_dump())
    item.creator_id = user_id
    item.done = False
    
    session.add(item)  
    await session.commit()
    await session.refresh(item)
    return item


async def delete_item_by_id(item_id: int, user_id: int, session: AsyncSession) -> None:
    item = await session.get(model.TodoItem, item_id)

    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    if item.creator_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this item")

    await session.delete(item)
    await session.commit()


