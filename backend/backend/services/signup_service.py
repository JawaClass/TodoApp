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


def send_signup_confirmation_email(email: str, base_url: str):
    
    text, html = create_confirmation_email_content(email, base_url, token_expire_minutes=30)

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


def create_confirmation_email_content(email: str, base_url: str, token_expire_minutes=30):
    access_token_expires = timedelta(minutes=token_expire_minutes)
    confirm_email_token = create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    ) 
    content = fmt_signup_confirmation_email_content(base_url, email, confirm_email_token)
    return content
 

def fmt_signup_confirmation_email_content(base_url: str, email: str, confirm_token: str): 
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
    
    return text, html
    