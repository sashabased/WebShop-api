from fastapi import FastAPI, APIRouter, Depends, status, HTTPException
from models import Cart
from schemas import CartBase, CartCreate, CartRead
from connection import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select
from uuid import UUID

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

@router.get("/", response_model=list[CartRead], status_code=200)
def get_all_carts(session: Session = Depends(get_db)):
    query = select(Cart)
    carts = session.scalars(query).all()

    if not carts:
        raise HTTPException(status_code=404)

    return carts

@router.post("/", response_model=CartRead, status_code=201)
def add_to_cart(
    cart_in: CartCreate, 
    session: Session = Depends(get_db)
):
    cart = session.scalar(select(Cart).where(Cart.user_id == cart_in.user_id, Cart.item_id == cart_in.item_id))
    data_to_put = cart_in.model_dump(exclude_defaults=True)

    if cart is None:
        cart = Cart(**data_to_put)
        session.add(cart)
    else:
        cart.items_count += 1

    session.commit()

    return cart

@router.delete("/{cart_id}", status_code=204)
def delete_cart_by_id(cart_id: UUID, session: Session = Depends(get_db)):
    cart = session.get(Cart, cart_id)
    
    if cart is None:
        raise HTTPException(status_code=404)
    else:
        session.delete(cart)

    session.commit()

@router.patch("/{cart_id}", status_code=200)
def edit_item_count_in_cart(cart_id: UUID, cart_in: CartBase, session: Session = Depends(get_db)):
    cart = session.get(Cart, cart_id)

    if cart is None:
        raise HTTPException(status_code=404)
    
    if cart_in.items_count == 0 or cart.items_count == 0:
        session.delete(cart)
        session.commit()
        return {"status": "success"}
    
    data_to_update = cart_in.model_dump(exclude_unset=True)

    for key, value in data_to_update.items():
        setattr(cart, key, value)

    session.commit()
    session.refresh(cart)

    return {
        "items_count": cart.items_count,
        "id": cart.id,
        "item": cart.item
    }
  