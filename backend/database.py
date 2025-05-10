import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from models.todo_item import SqlAlchemyBase

DATABASE_URL = "sqlite+aiosqlite:///./test.db"  # or use PostgreSQL, etc.

engine = create_async_engine(DATABASE_URL, echo=True)
sync_engine = create_engine("sqlite:///./test.db")

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

SqlAlchemyBase.metadata.drop_all(sync_engine)
SqlAlchemyBase.metadata.create_all(sync_engine)
