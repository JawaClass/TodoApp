from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

from backend.models import model

class TodoItemIn(BaseModel):
    channel_id: int | None = None
    name: str
    description: str 


class TodoItemUpdate(TodoItemIn):
    channel_id: int | None = None
    name: str | None = None
    description: str | None = None
    done: bool | None = None


class TodoItemOut(TodoItemIn):
    id: int
    creator_id: int
    create_date: datetime
    due_date: datetime 
    done: bool


class TodoItemOut_Detailed(TodoItemOut): 
    ref_creator: UserOut
    ref_channel: TodoItemChannelOut | None = None
    xxxx: str | None = Field(default=None)
    inner_str : list[str] = []
    inner_inner_str : list[list[str]] = []


class TodoItemDelete(BaseModel):
    id: int

class TodoItemChannelOut(BaseModel):
    id: int
    creator_id: int
    name: str
    description: str
    create_date: datetime

class UserIn(BaseModel): 
    name: str | None = None
    email: EmailStr
    password: str


class UserOut(BaseModel): 
    id: int
    name: str | None = None
    email: EmailStr
    role: model.UserRole
    disabled: bool
    email_verified: bool
    comment: str | None = None
    auth_provider: model.AuthProvider


class UserEdit(BaseModel):
    name: str | None = None
    password: str


class UserEdit_ByAdmin(BaseModel):
    # password: str   
    role: model.UserRole | None = None
    disabled: bool | None = None
    email_verified: bool | None = None

class UserIn_ByAdmin(UserIn): 
    role: model.UserRole | None = None
    disabled: bool | None = None
    email_verified: bool | None = None

class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str


class SimpleResponse(BaseModel):
    response: str