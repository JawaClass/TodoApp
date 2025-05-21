from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.routes.util.pagination import Page, PaginationParams, get_pagination_params
from backend.models import api
from backend.services.api import require_service, ServiceType
from backend.models import model

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.services.api.todo_item_service import TodoService


service = require_service(
    service_type=ServiceType.TodoItemService, user_role=model.UserRole.User
)

router = APIRouter(
    prefix="/todo-item", tags=["todo-item"], dependencies=[Depends(service)]
)


@router.get("{item_id}", response_model=api.TodoItemOut_Detailed)
async def get_by_id(item_id: int, service: TodoService = Depends(service)):
    item = await service.get_by_id(item_id, mask_class=api.TodoItemOut_Detailed)
    return item


@router.delete("{item_id}", response_model=api.SimpleResponse)
async def delete_item(item_id: int, service: TodoService = Depends(service)):
    _ = await service.delete_by_id(item_id)
    return api.SimpleResponse(response=f"Item {item_id=} deleted")


@router.post("", response_model=api.TodoItemOut)
async def create_new(item: api.TodoItemIn, service: TodoService = Depends(service)):
    new_item = await service.add(item)
    return new_item


@router.put("{item_id}", response_model=api.TodoItemOut_Detailed)
async def update_item(
    item_id: int,
    item_update: api.TodoItemUpdate,
    service: TodoService = Depends(service),
):
    result = await service.update(item_update, id=item_id)
    result = await service.get_by_id(result.id, mask_class=api.TodoItemOut_Detailed)
    return result


@router.get("", response_model=Page[api.TodoItemOut])
async def get_all(
    service: TodoService = Depends(service),
    params: PaginationParams = Depends(get_pagination_params),
):
    page = await service.get_all(params)
    return page
