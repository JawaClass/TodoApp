from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from backend.services.api import ServiceType, require_service
from backend.services import signup_service
from backend.models import model, api
from backend.services.api.user_service import UserService


service_without_user = require_service(
    service_type=ServiceType.UserService, user_role=None
)

service = require_service(
    service_type=ServiceType.UserService, user_role=model.UserRole.User
)

router = APIRouter(prefix="/signup")


@router.post("/repeat-send-confirm-email", response_model=api.SimpleResponse)
async def repeat_end_confirm_email(
    background_tasks: BackgroundTasks,
    request: Request,
    service: UserService = Depends(service),
):
    user = service.user
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User's email already verified!",
        )

    background_tasks.add_task(
        signup_service.send_signup_confirmation_email,
        email=user.email,
        base_url=str(request.base_url),
    )

    return api.SimpleResponse(response="Email sent")


@router.post("/user", response_model=api.SimpleResponse)
async def signup_user(
    signup_request: api.UserSignupRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    service: UserService = Depends(service_without_user),
):
    email = signup_request.email
    existing_user = await service.get_user_by(email=email)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )

    _ = await service.add_new_user(**signup_request)

    background_tasks.add_task(
        signup_service.send_signup_confirmation_email,
        email=email,
        base_url=str(request.base_url),
    )

    return api.SimpleResponse(response="Email sent")


@router.get("/confirm-email", response_model=api.SimpleResponse)
async def confirm_email(
    token: str,
    service: UserService = Depends(service_without_user),
):
    _ = await service.confirm_email(token)
    return api.SimpleResponse(response="Email successfully verified!")
