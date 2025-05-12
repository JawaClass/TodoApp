import asyncio
import pathlib
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from backend.models.model import SqlAlchemyBase

module_path = pathlib.Path(__file__).resolve().parent

db_path = module_path / "test.db"

ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{db_path}" 
SYNC_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
sync_engine = create_engine(SYNC_DATABASE_URL, echo=True) 

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


SqlAlchemyBase.metadata.drop_all(sync_engine)
SqlAlchemyBase.metadata.create_all(sync_engine)
