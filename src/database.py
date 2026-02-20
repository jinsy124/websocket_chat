from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./chat.db"  # Change to your DB if needed

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session