import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import Depends

# Default PostgreSQL connection string formatting:
# postgresql+asyncpg://user:password@host:port/dbname
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://jinsy:123456789@localhost:5432/postgres")
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
