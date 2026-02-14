from fastapi import FastAPI, APIRouter, HTTPException, Depends, responses, status
from models import User
from schemas import UserBase, UserCreate, UserRead, UserUpdate
from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select

router = APIRouter(
    prefix="/users",
    tags=["users"]              
)

@router.get("/", response_model=list[UserRead], status_code=200)
async def get_all_users(session: AsyncSession = Depends(get_db)):
    users = await session.scalars(select(User))
    users_all = users.all()

    if not users_all:
        raise HTTPException(status_code=404)
        
    return users_all
    
@router.get("/{user_id}", response_model=UserCreate, status_code=200)
async def get_user_by_id(user_id: UUID, session: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    user = await session.scalar(query)

    if user is None:
         raise HTTPException(status_code=404)
    
    return user

@router.post("/", response_model=UserRead,status_code=201)
async def add_user(user_in: UserCreate, session: AsyncSession = Depends(get_db)):
    new_user = User(**user_in.model_dump())
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    
    return new_user

@router.delete("/{user_id}", status_code=204)
async def delete_user_by_id(user_id: UUID, session: AsyncSession = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    user = await session.scalar(query)

    if user is None:
        raise HTTPException(status_code=404)
    
    session.delete(user)
    await session.commit()

@router.patch("/{user_id}", response_model=UserRead, status_code=200)
async def patch_user_by_id(user_id: UUID, user_in: UserUpdate, session: AsyncSession = Depends(get_db)):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404)

    update_data = user_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    await session.commit()
    await session.refresh(user)

    return user