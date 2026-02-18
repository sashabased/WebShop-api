from fastapi import FastAPI, APIRouter, HTTPException, Depends, responses, status

from models import Order, Order_Item, Cart, Item
from schemas import OrderItemRead, OrderRead, CartRead
from service.order import OrderService

from connection import get_db
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from uuid import UUID

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(user_id: UUID, session: AsyncSession = Depends(get_db)):
    try:
        order = await OrderService.create_order(user_id, session)

        if order is None:
            raise HTTPException(status_code=404, detail="cart is empty")
        
        return order
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=list[OrderRead], status_code=200)
async def get_user_orders(user_id: UUID, session: AsyncSession = Depends(get_db)):
    user_order = await OrderService.get_order_data(user_id, session)
    if user_order is None:
        raise HTTPException(status_code=404, detail="order not found or deleted")
    return user_order