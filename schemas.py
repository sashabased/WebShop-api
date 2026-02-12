from pydantic import BaseModel, Field, field_serializer, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

# User table validation

class UserBase(BaseModel):
    email: str
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: Optional[UUID]
    created_at: datetime | None = None

    @field_serializer('created_at')
    def format_datetime(self, dt: datetime):
        if dt is None:
            return None
        return (dt.strftime('%Y-%m-%d %H:%M'))

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

# Item table validation

class ItemBase(BaseModel):
    name: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    quantity: int = Field(ge=0)
    price: int = Field(ge=0)

    model_config = ConfigDict(from_attributes=True)

class ItemCreate(ItemBase):
    pass

class ItemRead(ItemBase):
    id: UUID

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[int] = None
    quantity: Optional[int] = None
    description: Optional[str] = None

# Cart table validation

class CartBase(BaseModel):
    items_count: Optional[int] = Field(default=1, ge=0)

    model_config = ConfigDict(from_attributes=True)

class CartCreate(CartBase):
    user_id: UUID
    item_id: UUID

class CartRead(CartBase):
    id: UUID
    item: ItemRead

# Order items table validation

class OrderItemRead(BaseModel):
    quantity: int
    price_on_purchase: int
    item: ItemRead

    model_config = ConfigDict(from_attributes=True)

# Orders table validation

class OrderRead(BaseModel):
    id: UUID
    overall_price: int
    order_date: datetime
    @field_serializer("order_date")
    def formate_datetime(self, dt: datetime):
        if dt is None:
            return None
        return (dt.strftime('%Y-%m-%d %H-%M'))

    order_item: list[OrderItemRead]

    model_config = ConfigDict(from_attributes=True)
