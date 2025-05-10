from sqlalchemy import (
    Enum,
    ForeignKey,
    SmallInteger,
    UniqueConstraint,
    DateTime,
    Text,
    String,
    VARCHAR,
    Date,
    func,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
import enum
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase

class BaseMixin:
    pass

class SqlAlchemyBase(DeclarativeBase, BaseMixin):

    def __str__(self) -> str:
        package = self.__class__.__module__
        class_ = self.__class__.__name__
        attrs = ((k, getattr(self, k)) for k in self.__mapper__.columns.keys())
        sattrs = ", ".join(f"{key}={value!r}" for key, value in attrs)
        return f"{package}.{class_}({sattrs})"

    def __repr__(self) -> str:
        return str(self)


class User(SqlAlchemyBase):
    __tablename__ = "user"

    # keys
    id: Mapped[int] = mapped_column(primary_key=True) 

    # scalars
    name: Mapped[str] = mapped_column(String(255), unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    hashed_password: Mapped[str] = mapped_column(Text)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    disabled: Mapped[bool] = mapped_column(SmallInteger, default=False)
    
    # refs
    # this users todo items created by them
    ref_todo_items: Mapped[list["TodoItem"]] = relationship("TodoItem", back_populates="ref_creator")

    # subscribed todo items (via item subscription table)
    ref_todo_item_subscriptions: Mapped[list["TodoItemUserSubscription"]] = relationship("TodoItemUserSubscription", back_populates="ref_user")
    
    # subscribed todo item channels (via channel subscription table)
    ref_todo_channel_subscriptions: Mapped[list["TodoChannelUserSubscription"]] = relationship("TodoChannelUserSubscription", back_populates="ref_user")


class TodoItemChannel(SqlAlchemyBase):
    __tablename__ = "todo_item_channel"
    __table_args__ = (UniqueConstraint("name", ),)

    # keys
    id: Mapped[int] = mapped_column(primary_key=True) 
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    # scalars
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # refs
    ref_creator: Mapped[User] = relationship()
    ref_items: Mapped[list["TodoItem"]] = relationship("TodoItem", back_populates="ref_channel")


class TodoItem(SqlAlchemyBase):
    __tablename__ = "todo_item"
    __table_args__ = (UniqueConstraint("name", "creator_id"),)

    # keys
    id: Mapped[int] = mapped_column(primary_key=True)
    creator_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    channel_id: Mapped[int | None] = mapped_column(
        ForeignKey("todo_item_channel.id", ondelete="CASCADE")
    )

    # scalars
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    create_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    due_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    done: Mapped[bool] = mapped_column(SmallInteger)   

    # refs
    ref_creator: Mapped[User] = relationship("User", back_populates="ref_creator")
    ref_channel: Mapped[TodoItemChannel | None] = relationship("TodoItemChannel", back_populates="ref_items")


class TodoItemUserSubscription(SqlAlchemyBase):
    __tablename__ = "todo_item_user_subscription"
    __table_args__ = (UniqueConstraint("user_id", "todo_item_id"),)

    # keys
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    todo_item_id: Mapped[int] = mapped_column(
        ForeignKey("todo_item.id", ondelete="CASCADE")
    )

    # scalars
    start_date_subscription: Mapped[str] = mapped_column(DateTime, server_default=func.now())

    # refs
    ref_user: Mapped[User] = relationship("User", back_populates="ref_todo_item_subscriptions")


class TodoChannelUserSubscription(SqlAlchemyBase):
    __tablename__ = "todo_channel_user_subscription"
    __table_args__ = (UniqueConstraint("user_id", "todo_item_channel_id"),)
    
    # keys
    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )
    todo_item_channel_id: Mapped[int] = mapped_column(
        ForeignKey("todo_item_channel.id", ondelete="CASCADE")
    )

    # scalars
    start_date_subscription: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # refs
    ref_user: Mapped[User] = relationship("User", back_populates="ref_todo_channel_subscriptions")







 

