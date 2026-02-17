from models import Item
from schemas import ItemBase, ItemCreate, ItemRead, ItemUpdate

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

class ItemService:

    @staticmethod
    async def get_all_items(session: AsyncSession):
        all_items = await session.scalars(select(Item))
        all_items_data = all_items.all()

        return all_items_data
    
    @staticmethod
    async def get_item_by_id(item_id: UUID, session: AsyncSession):
        return await session.scalar(select(Item).where(Item.id == item_id))
    
    @staticmethod
    async def add_item_to_shop(item_in: ItemCreate, session: AsyncSession):
        item_model = Item(**item_in.model_dump())
        session.add(item_model)
        await session.commit()
        await session.refresh(item_model)

        return item_model

    @staticmethod
    async def delete_item_by_id(item_id: UUID, session: AsyncSession):
        item_to_delete = await session.get(Item, item_id)
        
        if not item_to_delete:
            return False
        
        session.delete(item_to_delete)
        await session.commit()

        return True
    
    @staticmethod
    async def update_item_by_id(item_id: UUID, item_in: ItemUpdate, session: AsyncSession):
        item_to_upd = await session.get(Item, item_id)

        if item_to_upd is None:
            return None
        
        item_model = item_in.model_dump(exclude_unset=True)
        for key, value in item_model.items():
            setattr(item_to_upd, key, value)

        await session.commit()
        await session.refresh(item_to_upd)

        return item_to_upd