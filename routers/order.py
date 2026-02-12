from fastapi import FastAPI, APIRouter, HTTPException, Depends, responses, status
from models import Order, Order_Item, Cart, Item
from schemas import OrderItemRead, OrderRead, CartRead
from connection import get_db
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from sqlalchemy import select

router = APIRouter(
    prefix="/order",
    tags=["order"]
)

@router.post("/", status_code=201)
def create_order(user_id: UUID, session: Session = Depends(get_db)):
    items_pull = session.scalars(
        select(Cart).options(joinedload(Cart.item))
        .where(user_id == Cart.user_id)
    ).all()
    item_delete_bought = session.scalar(select(Item).where())

    if not items_pull:
        raise HTTPException(status_code=404, detail="Cart is empty.")

    new_order = Order(
        user_id=user_id,
        overall_price=0
    )
    session.add(new_order)
    session.flush()

    for items in items_pull:
        items.item.quantity -= items.items_count

        if items.item.quantity < 0:
            raise HTTPException(status_code=404, detail=f"Items quantity zero or below: {items.item.name}")
        
        new_order.overall_price += items.item.price * items.items_count
        order_item = Order_Item(
            quantity = items.items_count,
            price_on_purchase = items.item.price,
            item_id = items.item_id,
            order_id = new_order.id
        )
        session.add(order_item)
        session.delete(items)

    session.commit()
    session.refresh(new_order)
    
    return new_order

@router.get("/{user_id}", status_code=201)
def get_user_orders(user_id: UUID, session: Session = Depends(get_db)):
    all_orders = session.scalars(
        select(Order).options(joinedload(Order.order_item)
        .joinedload(Order_Item.item))
        .where(Order.user_id == user_id)
    ).unique().all()

    return all_orders
