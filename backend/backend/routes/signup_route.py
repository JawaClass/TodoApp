from datetime import timedelta
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jwt import PyJWTError
from pydantic import BaseModel, EmailStr
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from pprint import pprint
from jwt.exceptions import DecodeError

from backend.email import gmail_client 
from backend.services import user_service
from backend.services.auth_service import create_access_token, decode_access_token
from backend.database import async_session, get_session
from backend.models import model

router = APIRouter(prefix="/signup")

SIGNUP_TOKEN_EXPIRE_MINUTES = 30

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/user", response_model=str)
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
    
    access_token_expires = timedelta(minutes=SIGNUP_TOKEN_EXPIRE_MINUTES)
    confirm_email_token = create_access_token(
        data={"sub": new_user.email}, expires_delta=access_token_expires
    ) 

    background_tasks.add_task(send_signup_confirmation_email,
                              email=email,
                              **get_signup_confirmation_email_content(str(request.base_url), email, confirm_email_token))

    return Response(content="Confirmation email sent!", status_code=status.HTTP_200_OK)


@router.get("/confirm-email", response_model=str)
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

    return Response("Email successfully verified!", status_code=status.HTTP_200_OK)


def send_signup_confirmation_email(email: str, text: str, html: str):
    
    # Create a multipart message to support both plain text and HTML
    message = MIMEMultipart("alternative")

    # Add plain text part (for email clients that don't support HTML)
    text_part = MIMEText(text, "plain")
    message.attach(text_part)
    
    # Add HTML part (for email clients that support HTML)
    html_part = MIMEText(html, "html")
    message.attach(html_part)
    
    message["To"] = email
    message["From"] = "apptodo204@gmail.com"
    message["Subject"] = "Confirm email"

    gmail_client.send_email(message)


def get_signup_confirmation_email_content(base_url: str, email: str, confirm_token: str): 
    base_url = base_url[:-1] if base_url.endswith("/") else base_url
    link = f"{base_url}/signup/confirm-email?token={confirm_token}"

      # Return the email content in HTML format
    html = f"""
    <html>
    <body>
        <p>Hello <strong>{email}</strong>,</p>
        <p>Your signup is almost complete. Please click the link below to confirm your account:</p>
        <p>
            <a href="{link}" style="color: #ffffff; background-color: #4CAF50; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                Confirm Your Email
            </a>
        </p>
        <p>If you did not request this, please ignore this email.</p>
        <br>
        <p>Thank you!</p>
    </body>
    </html>
    """

    text = f"""Hello {email},
your signup is almost complete. Please click this link to confirm your Account.
    {link}
"""
    
    return {
        "text": text,
        "html": html
    }
    
