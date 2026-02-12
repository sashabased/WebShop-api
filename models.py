from uuid import UUID, uuid4
from typing import List, Optional
from sqlalchemy import ForeignKey, String, DateTime, func, TIMESTAMP, text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID

# main class
class Base(DeclarativeBase):
    pass

# User model
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(
        timezone=True),
        default=func.now()
    )

    cart_items: Mapped[List["Cart"]] = relationship(back_populates="user")
    user_in_order: Mapped[List["Order"]] = relationship(back_populates="user")

# Item model
class Item(Base):
    __tablename__ = "items"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100))
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(String(1000))

    cart_items: Mapped[List["Cart"]] = relationship(back_populates="item")
    item_in_order: Mapped[List["Order_Item"]] = relationship(back_populates="item")

# Cart model

class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    items_count: Mapped[int] = mapped_column(Integer, default=1)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="cart_items")
    item: Mapped["Item"] = relationship(back_populates="cart_items")

# Order model

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    order_date: Mapped[datetime] = mapped_column(DateTime(
        timezone=True),
        default=func.now()
    )
    overall_price: Mapped[int] = mapped_column(Integer)

    order_item: Mapped[List["Order_Item"]] = relationship(back_populates="order_part")
    user: Mapped["User"] = relationship(back_populates="user_in_order")
    
class Order_Item(Base):
    __tablename__ = "order_items"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    quantity: Mapped[int] = mapped_column(Integer)
    price_on_purchase: Mapped[int] = mapped_column(Integer)

    item_id: Mapped[UUID] = mapped_column(ForeignKey("items.id"))
    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"))

    order_part: Mapped["Order"] = relationship(back_populates="order_item")
    item: Mapped["Item"] = relationship(back_populates="item_in_order")