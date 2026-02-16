from fastapi import APIRouter, HTTPException, Depends

from models import User
from schemas import UserCreate, UserRead, UserUpdate
from service.users import UserService

from connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from uuid import UUID

router = APIRouter(
    prefix="/users",
    tags=["users"]              
)

@router.get("/", response_model=list[UserRead], status_code=200)
async def get_all_users(session: AsyncSession = Depends(get_db)):
    all_users = await UserService.get_all_users(session)
    if not all_users:
        raise HTTPException(status_code=404, detail="database have no users")

    return all_users
    
@router.get("/{user_id}", response_model=UserRead, status_code=200)
async def get_user_by_id(user_id: UUID, session: AsyncSession = Depends(get_db)):
    user = await UserService.get_user_by_id(user_id, session)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")

    return user

@router.post("/", response_model=UserRead,status_code=201)
async def add_user(user_in: UserCreate, session: AsyncSession = Depends(get_db)):

    return await UserService.create_new_user(user_in, session)

@router.delete("/{user_id}", status_code=204)
async def delete_user_by_id(user_id: UUID, session: AsyncSession = Depends(get_db)):
    success = await UserService.delete_user_by_id(user_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="user id is wrong or doesnt exists")

@router.patch("/{user_id}", response_model=UserRead, status_code=200)
async def patch_user_by_id(user_id: UUID, user_in: UserUpdate, session: AsyncSession = Depends(get_db)):
    user = await UserService.update_user_by_id(user_id, user_in, session)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return user