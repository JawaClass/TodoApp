from fastapi import APIRouter, Depends, Request
from backend.services.api.user_google_service import UserGoogleService
from backend.services.api import ServiceType, require_service
from backend.models.auth_model import Token
from backend.models import model
from fastapi_sso.sso.google import GoogleSSO
from backend.env import environment


CLIENT_ID = environment("GOOGLE_CLIENT_ID")
CLIENT_SECRET = environment("GOOGLE_CLIENT_SECRET")

sso = GoogleSSO(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri="http://localhost:8000/authentication/auth-google/callback",
    allow_insecure_http=True,
)

service = require_service(
    service_type=ServiceType.UserGoogleService, user_role=model.UserRole.User
)

service_without_user = require_service(
    service_type=ServiceType.UserGoogleService, user_role=None
)


router = APIRouter(prefix="/auth-google")


@router.get("/login")
async def auth_init():
    """Initialize Google auth and redirect"""
    async with sso:
        return await sso.get_login_redirect(
            params={"prompt": "consent", "access_type": "offline"}
        )


@router.get("/callback", response_model=Token, name="auth_google_callback")
async def auth_callback(
    request: Request, service: UserGoogleService = Depends(service_without_user)
):
    """Verify google login"""
    async with sso:
        google_user = await sso.verify_and_process(request)

        db_user = await service.get_user_by(email=google_user.email)

        if not db_user:
            db_user = await service.add_new_user(google_user.email)

    service.user = db_user

    token = await service.create_bearer_token()

    return token
