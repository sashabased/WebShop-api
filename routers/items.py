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
    return await ItemService.add_item_to_shop(item_in, session)

@router.delete("/{item_id}", status_code=204)
async def delete_item_by_id(item_id: UUID, session: AsyncSession = Depends(get_db)):
    result = await ItemService.delete_item_by_id(item_id, session)
    if not result:
        raise HTTPException(status_code=404, detail="item id is wrong or doesnt exists")
    

@router.patch("/{item_id}", response_model=ItemRead, status_code=200)
async def update_item_by_id(
    item_id: UUID,
    item_in: ItemUpdate, 
    session: AsyncSession = Depends(get_db)
):
    item = await ItemService.update_item_by_id(item_id, item_in, session)
    if item is None:
        raise HTTPException(status_code=404, detail="item id not found")
    return item