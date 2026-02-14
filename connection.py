from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine("postgresql+asyncpg://postgres:19762003@db:5432/shop_db", echo=True)
SessionLocal = sessionmaker(
    bind=engine, 
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False
)

async def get_db():
    async with SessionLocal() as session:
        yield session