from fastapi import APIRouter
from . import auth_google_user_route, auth_local_user_route


router = APIRouter(prefix="/authentication", tags=["authentication"])

router.include_router(auth_google_user_route.router) 
router.include_router(auth_local_user_route.router) 