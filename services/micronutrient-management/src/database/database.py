from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from ..models.micronutrient_models import Base

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/micronutrients_db"

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool, # Use NullPool for FastAPI to manage connections per request
    future=True
)

AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session