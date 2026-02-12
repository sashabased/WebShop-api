from fastapi import FastAPI, APIRouter, HTTPException, Depends, responses, status
from models import User
from schemas import UserBase, UserCreate, UserRead, UserUpdate
from connection import get_db
from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy import select

router = APIRouter(
    prefix="/users",
    tags=["users"]              
)

@router.get("/", response_model=list[UserRead], status_code=200)
def get_all_users(session: Session = Depends(get_db)):
    query = select(User)
    users = session.scalars(query).all()

    if users is None:
        raise HTTPException(status_code=404)
        
    return users
    
@router.get("/{user_id}", response_model=UserCreate, status_code=200)
def get_user_by_id(user_id: UUID, session: Session = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    user = session.scalars(query).first()

    if user is None:
         raise HTTPException(status_code=404)
    
    return user

@router.post("/", response_model=UserRead,status_code=201)
def add_user(user_in: UserCreate, session: Session = Depends(get_db)):
    new_user = User(**user_in.model_dump())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return new_user

@router.delete("/{user_id}", status_code=204)
def delete_user_by_id(user_id: UUID, session: Session = Depends(get_db)):
    query = select(User).where(User.id == user_id)
    user = session.scalar(query)

    if user is None:
        raise HTTPException(status_code=404)
    
    session.delete(user)
    session.commit()

@router.patch("/{user_id}", response_model=UserRead, status_code=200)
def patch_user_by_id(user_id: UUID, user_in: UserUpdate, session: Session = Depends(get_db)):
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404)

    update_data = user_in.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(user, key, value)

    session.commit()
    session.refresh(user)

    return user
