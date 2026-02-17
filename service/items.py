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