from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.auth_service import get_current_active_user
from backend.database import get_session
from sqlalchemy import func, select, Select
from backend.models.model import User
from backend.models import api
from fastapi import Query, Depends
from pydantic import BaseModel
from typing import Any, Optional
from math import ceil
from sqlalchemy.ext.asyncio import AsyncSession
from backend.routes.util.pagination import Page, PaginationParams, get_pagination_params, paginate_query

router = APIRouter(prefix="/user") # , dependencies=[Depends(get_current_active_user)]
 
@router.get("", response_model=Page[api.UserOut])
async def get_all(
    session: AsyncSession = Depends(get_session),
    params: PaginationParams = Depends(get_pagination_params),
):
    stmt = select(User)
    page = await paginate_query(stmt, session, params)
    return page 
