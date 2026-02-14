from fastapi import FastAPI, APIRouter, Depends, status, HTTPException
from models import Cart
from schemas import CartBase, CartCreate, CartRead
from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/cart",
    tags=["cart"]
)

@router.get("/", response_model=list[CartRead], status_code=200)
async def get_all_carts(session: AsyncSession = Depends(get_db)):
    result = await session.scalars(
        select(Cart)
        .options(joinedload(Cart.item))
    )
    carts = result.all()

    if not carts:
        raise HTTPException(status_code=404)

    return carts

@router.get("/{user_id}", response_model=list[CartRead], status_code=200)
async def get_user_cart(user_id: UUID, session: AsyncSession = Depends(get_db)):
    cart_items = await session.scalars(
        select(Cart)
        .options(joinedload(Cart.item))
        .where(user_id == Cart.user_id)
    )

    all_cart_items = cart_items.all()

    if not all_cart_items:
        raise HTTPException(status_code=404, detail="User dont have items in cart or cart doesnt exists.")

    return all_cart_items

@router.post("/", response_model=CartRead, status_code=201)
async def add_to_cart(
    cart_in: CartCreate, 
    session: AsyncSession = Depends(get_db)
):
    cart = await session.scalar(
        select(Cart)
        .options(joinedload(Cart.item))
        .where(
            Cart.user_id == cart_in.user_id, 
            Cart.item_id == cart_in.item_id
        )
    )
    data_to_put = cart_in.model_dump(exclude_defaults=True)

    if cart is None:
        cart = Cart(**data_to_put)
        session.add(cart)
    else:
        cart.items_count += 1

    await session.commit()
    await session.refresh(cart)

    return cart

@router.delete("/{cart_id}", status_code=204)
async def delete_cart_by_id(cart_id: UUID, session: AsyncSession = Depends(get_db)):
    cart = await session.get(Cart, cart_id)
    
    if cart is None:
        raise HTTPException(status_code=404)
    else:
        session.delete(cart)

    await session.commit()

@router.patch("/{cart_id}", status_code=200)
async def edit_item_count_in_cart(
    cart_id: UUID,
    cart_in: CartBase,
    session: AsyncSession = Depends(get_db)
):
    async with session.begin():
        cart = await session.scalar(
            select(Cart)
            .options(joinedload(Cart.item))
            .where(Cart.id == cart_id)
        )

        if cart is None:
            raise HTTPException(status_code=404)
        
        if cart_in.items_count == 0 or cart.items_count == 0:
            await session.delete(cart)
            return {"status": "item deleted from the cart"}
        
        data_to_update = cart_in.model_dump(exclude_unset=True)

        for key, value in data_to_update.items():
            setattr(cart, key, value)

    await session.refresh(cart)
    return {
        "items_count": cart.items_count,
        "id": cart.id,
        "item": cart.item
    }