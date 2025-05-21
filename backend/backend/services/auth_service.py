from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext 
from backend.models import model
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_session
import jwt

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

CREDENTIALS_EXCEPTION = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/auth-local/token")


async def get_user_by_email(email: str, session: AsyncSession):
    from backend.services.api import user_service
    service = user_service.UserService(session, user=None)
    return await service.get_user_by(email=email)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str):
    return pwd_context.hash(password)


async def authenticate_user(email: str, password: str, session: AsyncSession): 
    user = await get_user_by_email(email, session)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
 

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           session: AsyncSession = Depends(get_session),):
    print("get_current_user....")
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise CREDENTIALS_EXCEPTION
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION
    user = await get_user_by_email(email, session)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    return user
 

async def get_current_active_user(
    current_user: Annotated[model.User, Depends(get_current_user)],
):  
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_active_verified_user(
    current_user: Annotated[model.User, Depends(get_current_active_user)],
):  
    if not current_user.email_verified:
        raise HTTPException(status_code=400, detail="Email not verified") 
    return current_user


async def get_admin_user(
    current_user: Annotated[model.User, Depends(get_current_active_user)],
):  
    print("get_admin_user...", current_user)
    if current_user.role != model.UserRole.Admin:
        raise HTTPException(status_code=400, detail="Not admin")
    return current_user
