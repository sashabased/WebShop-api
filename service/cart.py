from models import Cart, Item
from schemas import CartBase, CartCreate, CartRead

from sqlalchemy.orm import joinedload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

class CartService:

    @staticmethod
    async def get_all_carts(session: AsyncSession):
        carts = await session.scalars(select(Cart).options(joinedload(Cart.item)))
        carts_data = carts.all()

        return carts_data
    
    @staticmethod
    async def get_cart_by_id(user_id: UUID, session: AsyncSession):
        items = await session.scalars(
            select(Cart)
            .options(joinedload(Cart.item))
            .where(Cart.user_id == user_id)
        )

        all_user_items = items.all()

        for item in all_user_items:
            if item.items_count > item.item.quantity:
                if item.item.quantity != 0:
                    item.items_count = item.item.quantity
                elif item.item.quantity == 0:
                    item.items_count = 0

        await session.commit()

        return all_user_items

    @staticmethod
    async def create_cart(cart_in: CartCreate, session: AsyncSession):
        cart = await session.scalar(
            select(Cart)
            .options(joinedload(Cart.item))
            .where(
                Cart.item_id == cart_in.item_id,
                Cart.user_id == cart_in.user_id
            )
        )

        item_to_check = await session.scalar(
            select(Item)
            .where(cart_in.item_id == Item.id)
            )

        cart_model = cart_in.model_dump()
        
        if cart is None:
            if cart_in.items_count > item_to_check.quantity:
                raise ValueError("not enought items to add for cart")
            else:
                cart = Cart(**cart_model)
                session.add(cart)
        else:
            cart.items_count += cart_in.items_count
            if cart.items_count > item_to_check.quantity:
                cart.items_count -= cart_in.items_count
                raise ValueError("not enought items to add for cart")

        await session.commit()

        cart = await session.scalar(
            select(Cart)
            .options(joinedload(Cart.item))
            .where(
                Cart.item_id == cart_in.item_id,
                Cart.user_id == cart_in.user_id
            )
        )
        await session.refresh(cart)

        return cart
    
    @staticmethod
    async def delete_cart_by_id(cart_id: UUID, session: AsyncSession):
        cart_to_del = await session.get(Cart, cart_id)

        if not cart_to_del:
            return False
        
        session.delete(cart_to_del)
        await session.commit()

        return True
    
    @staticmethod
    async def update_item_count_by_id(cart_id: UUID, cart_in: CartBase, session: AsyncSession):
        status = False
        async with session.begin():
            cart_to_upd = await session.scalar(
                select(Cart)
                .options(joinedload(Cart.item))
                .where(Cart.id == cart_id)
            )
            if cart_to_upd is None:
                return None

            if cart_in.items_count == 0 or cart_to_upd.items_count <= 0:
                session.delete(cart_to_upd)
                return "deleted"

            cart_model = cart_in.model_dump(exclude_unset=True)

            for key, value in cart_model.items():
                setattr(cart_to_upd, key, value)

        await session.refresh(cart_to_upd)
        return cart_to_upd