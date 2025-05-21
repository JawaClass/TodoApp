from __future__ import annotations

from fastapi import APIRouter, Depends
from backend.services.api import require_service, ServiceType
from backend.routes.util.pagination import Page, PaginationParams, get_pagination_params
from backend.models import api
from backend.models import model
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from backend.services.api.user_service import UserService

service = require_service(
    service_type=ServiceType.UserService, user_role=model.UserRole.User
)

admin_service = require_service(
    service_type=ServiceType.UserService, user_role=model.UserRole.Admin
)

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=api.UserOut)
async def get_me(service: UserService = Depends(service)):
    return service.user


@router.get("", response_model=Page[api.UserOut])
async def get_all(
    service: UserService = Depends(admin_service),
    params: PaginationParams = Depends(get_pagination_params),
):
    user_list = await service.get_all(params)
    return user_list


@router.delete("", response_model=int)
async def disable_current_user(
    service: UserService = Depends(service),
):
    disabled_user = await service.disable_user()
    return disabled_user.id


@router.patch("", response_model=api.UserOut)
async def edit_user_self(
    user_edit: api.UserEdit,
    service: UserService = Depends(service),
):
    updated_user = await service.update(user_edit, entity=service.user)
    return updated_user


@router.patch("/{user_id}", response_model=api.UserOut)
async def edit_user_by_id(
    user_id: int,
    user_edit: api.UserEdit_ByAdmin,
    service: UserService = Depends(admin_service),
):
    user = await service.get_user_by(user_id=user_id)
    updated_user = await service.update(user_edit, entity=user)
    return updated_user


@router.post("", response_model=api.UserOut)
async def create_user(
    user_in: api.UserIn_ByAdmin,
    service: UserService = Depends(admin_service),
):
    user = await service.add(user_in)
    return user
