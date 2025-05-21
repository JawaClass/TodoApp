from fastapi import APIRouter
from . import todo_item, user_route, signup_route


router = APIRouter(prefix="/api", tags=["api"])

router.include_router(todo_item.router)
router.include_router(user_route.router)
router.include_router(signup_route.router)
