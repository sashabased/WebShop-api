from fastapi import FastAPI, APIRouter, Depends, status, HTTPException

from models import Cart
from schemas import CartBase, CartCreate, CartRead
from service.cart import CartService

from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from uuid import UUID

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

@router.get("/", response_model=list[CartRead], status_code=200)
async def get_all_carts(session: AsyncSession = Depends(get_db)):
    carts = await CartService.get_all_carts(session)
    if not carts:
        raise HTTPException(status_code=404, detail="carts not found")
    return carts

@router.get("/{user_id}", response_model=list[CartRead], status_code=200)
async def get_user_cart(user_id: UUID, session: AsyncSession = Depends(get_db)):
    cart = await CartService.get_cart_by_id(user_id, session)
    if not cart:
        raise HTTPException(status_code=404, detail="cart not found")
    return cart

@router.post("/", response_model=CartRead, status_code=201)
async def create_cart(
    cart_in: CartCreate, 
    session: AsyncSession = Depends(get_db)
):
    try:
        cart = await CartService.create_cart(cart_in, session) 
        if cart is None:
            raise HTTPException(status_code=404, detail="cart is none")
        return cart
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{cart_id}", status_code=204)
async def delete_cart_by_id(cart_id: UUID, session: AsyncSession = Depends(get_db)):
    result = await CartService.delete_cart_by_id(cart_id, session)
    if not result:
        raise HTTPException(status_code=404, detail="cart not found")

@router.patch("/{cart_id}", status_code=200)
async def edit_item_count_in_cart(
    cart_id: UUID,
    cart_in: CartBase,
    session: AsyncSession = Depends(get_db)
):
    cart_to_upd = await CartService.delete_cart_by_id(cart_id, cart_in, session)
    
    if cart_to_upd is None:
        raise HTTPException(status_code=404, detail="cart not found")
    if cart_to_upd == "deleted":
        return {"status": "cart was deleted success"}
    return cart_to_upd