from datetime import timedelta
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jwt import PyJWTError
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from backend.services import user_service
from backend.services import signup_service

from backend.services.auth_service import decode_access_token, get_current_active_user
from backend.database import async_session, get_session
from backend.models import model


router = APIRouter(prefix="/signup")

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str


class SimpleResponse(BaseModel):
    response: str


@router.post("/repeat-send-confirm-email", response_model=SimpleResponse)
async def repeat_end_confirm_email(
    background_tasks: BackgroundTasks,
    request: Request,
    user: model.User = Depends(get_current_active_user)
):   
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User's email already verified!"
        )

    background_tasks.add_task(signup_service.send_signup_confirmation_email,
                              email=user.email,
                              base_url=str(request.base_url)
                              )

    return SimpleResponse(response="Email sent")


@router.post("/user", response_model=SimpleResponse)
async def signup_user(
    signup_request: UserSignupRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
):  
    email = signup_request.email
    existing_user = await user_service.get_user_by_email(email, session)
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists."
        )
    
    new_user = await user_service.add_new_user(email, signup_request.password, session)
    
    background_tasks.add_task(signup_service.send_signup_confirmation_email,
                              email=email,
                              base_url=str(request.base_url)
                              )

    return SimpleResponse(response="Email sent")


@router.get("/confirm-email", response_model=SimpleResponse)
async def confirm_email(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        payload = decode_access_token(token)
    except PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token.")

    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=400, detail="Invalid token payload.")
    
    user = await user_service.get_user_by_email(email, session)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.email_verified:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email has already been verified!")
    
    user.email_verified = True

    session.add(user)
    await session.commit()

    return SimpleResponse(response="Email successfully verified!")

