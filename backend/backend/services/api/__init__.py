from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session
from backend.services import auth_service
import enum
from backend.models import model
from . import user_service, user_google_service, todo_item_service


class ServiceType(enum.Enum):
    UserService = enum.auto()
    UserGoogleService = enum.auto()
    TodoItemService = enum.auto()


user_role_2_getter = {
    model.UserRole.User: auth_service.get_current_active_verified_user,
    model.UserRole.Admin: auth_service.get_admin_user,
}


def require_service(
    service_type: ServiceType,
    user_role: model.UserRole | None = None,
):
    get_user = user_role_2_getter.get(user_role) or (lambda: None)

    async def dependency(
        db: AsyncSession = Depends(get_session), user: model.User = Depends(get_user)
    ):
        service = {
            ServiceType.UserService: user_service.UserService(db, user),
            ServiceType.UserGoogleService: user_google_service.UserGoogleService(
                db, user
            ),
            ServiceType.TodoItemService: todo_item_service.TodoService(db, user),
        }
        return service[service_type]

    return dependency
