from models import Order, Order_Item, Cart, Item
from schemas import OrderItemRead, OrderRead, CartRead

from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from uuid import UUID

class OrderService:

    @staticmethod
    async def create_order(user_id: UUID, session: AsyncSession):
        new_order = None
        async with session.begin():
            items_pull = await session.scalars(
                select(Cart)
                .options(joinedload(Cart.item))
                .where(Cart.user_id == user_id)
            )
            all_items_data = items_pull.all()

            if not all_items_data:
                return None

            new_order = Order(
                user_id = user_id,
                overall_price = 0
            )
            session.add(new_order)
            await session.flush()

            for items in all_items_data:

                if items.item.quantity <= 0 or items.item.quantity < items.items_count:
                    raise ValueError(f"Not enough stock for {items.item.name}")

                items.item.quantity -= items.items_count
                new_order.overall_price += items.items_count * items.item.price
                order_item = Order_Item(
                    quantity = items.items_count,
                    price_on_purchase = items.item.price,
                    item_id = items.item_id,
                    order_id = new_order.id
                )

                session.add(order_item)
                await session.delete(items)

        await session.scalar(
            select(Order)
            .options(selectinload(Order.order_item)
            .selectinload(Order_Item.item))
            .where(Order.user_id == user_id)
            )
        await session.refresh(new_order)
        return new_order
    
    @staticmethod
    async def get_order_data(user_id:UUID, session: AsyncSession):
        order = await session.scalars(
            select(Order)
            .options(selectinload(Order.order_item)
            .selectinload(Order_Item.item))
            .where(Order.user_id == user_id)
        )

        filtered_order = order.unique().all()

        if not filtered_order:
            return None

        return filtered_order