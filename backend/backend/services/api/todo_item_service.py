from backend.services.api.crud_base_auth_service import CrudBaseAuthService
from backend.routes.util.pagination import PaginationParams
from backend.models import model


class TodoService(CrudBaseAuthService[model.TodoItem]):
    def __init__(self, db, user: model.User):
        super().__init__(model.TodoItem, db, "id")
        self.user = user

    async def get_all(self, params: PaginationParams):
        return await super().get_all(
            params, where_clause=model.TodoItem.creator_id == self.user.id
        )

    async def can_delete(self, entity):
        return (
            self.user.id == entity.creator_id or self.user.role == model.UserRole.Admin
        )

    async def can_update(self, entity):
        return (
            self.user.id == entity.creator_id or self.user.role == model.UserRole.Admin
        )

    async def can_view(self, entity):
        return (
            self.user.id == entity.creator_id or self.user.role == model.UserRole.Admin
        )
