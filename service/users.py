from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID

from models import User
from schemas import UserCreate, UserUpdate

class UserService:
    
    @staticmethod
    async def create_new_user(user_data: UserCreate, session: AsyncSession):
        user_to_add = User(**user_data.model_dump())
        session.add(user_to_add)
        await session.commit()
        await session.refresh(user_to_add)

        return user_to_add

    @staticmethod
    async def get_all_users(session: AsyncSession):
        all_users = await session.scalars(select(User))
        all_user_data = all_users.all()

        return all_user_data

    @staticmethod
    async def get_user_by_id(user_id: UUID, session: AsyncSession):

        return await session.scalar(select(User).where(User.id == user_id))

    @staticmethod
    async def delete_user_by_id(user_id: UUID, session: AsyncSession):
        user_to_dlt = await session.get(User, user_id)

        if not user_to_dlt:
            return False
        
        session.delete(user_to_dlt)
        await session.commit()
        return True
    
    @staticmethod
    async def update_user_by_id(user_id: UUID, user_in: UserUpdate, session: AsyncSession):
        user_to_upd = await session.get(User, user_id)

        if user_to_upd is None:
            return None

        user_model = user_in.model_dump(exclude_unset=True)
        for key, value in user_model.items():
            setattr(user_to_upd, key, value)

        await session.commit()
        await session.refresh(user_to_upd)

        return user_to_upd