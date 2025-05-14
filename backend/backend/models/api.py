from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

class TodoItemIn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    channel_id: int | None = None
    name: str
    description: str
    

    # # refs
    # ref_creator: Mapped[User] = relationship("User", back_populates="ref_todo_items")
    # ref_channel: Mapped[TodoItemChannel | None] = relationship("TodoItemChannel", back_populates="ref_items")

class TodoItemOut(TodoItemIn):
    id: int
    creator_id: int
    create_date: datetime
    due_date: datetime 
    done: bool


class UserIn(BaseModel): 
    name: str | None = None
    email: EmailStr
    password: str


class UserOut(BaseModel): 
    id: int
    name: str | None = None
    email: EmailStr