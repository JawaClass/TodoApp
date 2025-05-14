from backend.backend.models.model import TodoItem, User


def can_view_item(user: User, item: TodoItem) -> bool:
    return item.creator_id == user.id or user.role == "admin"

def can_edit_item(user: User, item: TodoItem) -> bool:
    return item.creator_id == user.id