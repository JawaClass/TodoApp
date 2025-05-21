from datetime import timedelta
from sqlalchemy import select
from backend.services.api.crud_base_service import CrudBaseService
from backend.models import model
from fastapi import HTTPException, status
from backend.services.auth_service import (
    create_access_token,
    hash_password,
    decode_access_token,
)
from jwt import PyJWTError
from backend.models.auth_model import Token


class UserService(CrudBaseService):
    def __init__(self, db, user: model.User):
        super().__init__(model.User, db, "id")
        self.user = user

    async def get_user_by(
        self, /, email: str = None, user_id: int = None
    ) -> model.User | None:
        stmt = select(model.User)
        if email:
            stmt = stmt.where(model.User.email == email)
        elif user_id:
            stmt = stmt.where(model.User.id == user_id)
        else:
            self._ra
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Argument missing"
            )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def disable_user(self, user: model.User = None):
        user = user or self.user
        user.disabled = True
        return await self.save_entity(user)

    async def verify_user(self, user: model.User = None):
        user = user or self.user
        user.email_verified = True
        return await self.save_entity(user)

    async def add_new_user(self, /, email: str, password: str, **kwargs):
        user = model.User(
            email=email, hashed_password=hash_password(password), **kwargs
        )

        return await self.save_entity(user)

    async def confirm_email(self, token: str) -> None:
        try:
            payload = decode_access_token(token)
        except PyJWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token.")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token payload.")

        user = await self.get_user_by(email=email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.email_verified:
            raise HTTPException(
                status_code=404, detail="Email has already been verified!"
            )

        await self.verify_user(user)

    async def create_bearer_token(self, expire_minutes=30):
        access_token_expires = timedelta(minutes=expire_minutes)
        access_token = create_access_token(
            data={"sub": self.user.email}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
