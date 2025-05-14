from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.auth_service import get_current_active_verified_user
from backend.services import todo_item_service
from backend.database import get_session
from sqlalchemy import func, select, Select
from backend.models.model import TodoItem, User
from backend.models import api
from fastapi import Query, Depends
from pydantic import BaseModel
from typing import Any, Optional
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from backend.routes.util.pagination import Page, PaginationParams, get_pagination_params, paginate_query

router = APIRouter(prefix="/todo-item", dependencies=[Depends(get_current_active_verified_user)])
 

@router.get("", response_model=Page[api.TodoItemOut])
async def get_all(
    session: AsyncSession = Depends(get_session),
    params: PaginationParams = Depends(get_pagination_params),
    user: User = Depends(get_current_active_verified_user)
):
    page = await todo_item_service.get_all_for_user(user, session, params) 
    return page


@router.post("", response_model=api.TodoItemOut)
async def create_new(
    item: api.TodoItemIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_active_verified_user)
):
    new_item = await todo_item_service.add_new_item(item, user.id, session)
    # print("create_new....", item)
    return new_item
