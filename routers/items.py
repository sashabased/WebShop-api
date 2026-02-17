from fastapi import APIRouter, HTTPException, Depends

from models import Item
from schemas import ItemBase, ItemCreate, ItemRead, ItemUpdate
from service.items import ItemService

from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from uuid import UUID

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/", response_model=list[ItemRead])
async def get_items(session: AsyncSession = Depends(get_db)):
    items = await ItemService.get_all_items(session)
    if not items:
        raise HTTPException(status_code=404, detail="database have no items")
    return items

@router.get("/{item_id}", response_model=ItemRead, status_code=200)
async def get_item_by_id(item_id: UUID, session: AsyncSession = Depends(get_db)):
    item = await ItemService.get_item_by_id(item_id, session)
    if item is None:
        raise HTTPException(status_code=404, detail='item not found')
    return item

@router.post("/", response_model=ItemRead, status_code=201)
async def add_item_to_shop(item_in: ItemCreate, session: AsyncSession = Depends(get_db)):
    new_item = Item(**item_in.model_dump())
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)

    return new_item

@router.delete("/{item_id}", status_code=204)
async def delete_item_by_id(item_id: UUID, session: AsyncSession = Depends(get_db)):
    query = select(Item).where(Item.id == item_id)
    item_to_delete = await session.scalar(query)

    session.delete(item_to_delete)
    await session.commit()

@router.patch("/{item_id}", response_model=ItemRead, status_code=200)
async def update_item_by_id(
    item_id: UUID,
    item_in: ItemUpdate, 
    session: AsyncSession = Depends(get_db)
):
    item = await session.get(Item, item_id)

    if item is None:
        raise HTTPException(status_code=404)
    
    data_for_update = item_in.model_dump(exclude_unset=True)
    
    for key, value in data_for_update.items():
        setattr(item, key, value)

    await session.commit()
    await session.refresh(item)

    return item