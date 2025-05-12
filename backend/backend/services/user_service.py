from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.services.auth_service import hash_password
from backend.models import model

async def get_user_by_email(email: str, session: AsyncSession):
    result = await session.execute(select(model.User).where(model.User.email == email)) 
    return result.scalar_one_or_none()


async def add_new_user(email: str, password: str, session: AsyncSession):
    user = model.User(email=email,
                      hashed_password=hash_password(password),
                      email_verified=False,
                      disabled=False,
                      name=None)
    
    session.add(user)  
    await session.commit()
    await session.refresh(user)
    return user