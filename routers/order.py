from fastapi import FastAPI, APIRouter, HTTPException, Depends, responses, status
from models import Order, Order_Item, Cart, Item
from schemas import OrderItemRead, OrderRead, CartRead
from connection import get_db
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

@router.post("/", response_model=OrderRead, status_code=201)
async def create_order(user_id: UUID, session: AsyncSession = Depends(get_db)):
    async with session.begin():
        items_pull = await session.scalars(
            select(Cart).options(joinedload(Cart.item))
            .where(user_id == Cart.user_id)
        )
        all_items = items_pull.all()

        if not all_items:
            raise HTTPException(status_code=404, detail="Cart is empty.")

        new_order = Order(
            user_id=user_id,
            overall_price=0
        )
        session.add(new_order)
        await session.flush()

        for items in all_items:

            if items.item.quantity < 0 or items.item.quantity < items.items_count:
                raise HTTPException(status_code=404, detail=f"Items quantity zero: {items.item.name}")
            
            items.item.quantity -= items.items_count
            
            new_order.overall_price += items.item.price * items.items_count
            order_item = Order_Item(
                quantity = items.items_count,
                price_on_purchase = items.item.price,
                item_id = items.item_id,
                order_id = new_order.id
            )
            session.add(order_item)
            session.delete(items)
        
    await session.refresh(new_order)
    return new_order

@router.get("/{user_id}", response_model=list[OrderRead], status_code=201)
async def get_user_orders(user_id: UUID, session: AsyncSession = Depends(get_db)):
    all_orders = await session.scalars(
        select(Order).options(joinedload(Order.order_item)
        .joinedload(Order_Item.item))
        .where(Order.user_id == user_id)
    )
    filtered_orders = all_orders.unique().all()

    return filtered_orders