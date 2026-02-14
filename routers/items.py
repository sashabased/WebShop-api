from fastapi import FastAPI, APIRouter, HTTPException, Depends, Response, status
from models import Item
from schemas import ItemBase, ItemCreate, ItemRead, ItemUpdate
from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select

router = APIRouter(
    prefix="/items",
    tags=["items"]
)

@router.get("/", response_model=list[ItemRead])
async def get_items(session: AsyncSession = Depends(get_db)):
    query = select(Item)
    result = await session.scalars(query)
    items = result.all()
    
    if not items:
        raise HTTPException(status_code=404)
    
    return items

@router.get("/{item_id}", response_model=ItemRead, status_code=200)
async def get_item_by_id(item_id: UUID, session: AsyncSession = Depends(get_db)):
    query = select(Item).where(Item.id == item_id)
    item = await session.scalar(query)

    if item is None:
        raise HTTPException(status_code=404)

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