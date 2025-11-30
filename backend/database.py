import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Construct the Database URL from Environment Variables
# Terraform injects these variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# We use the postgresql+asyncpg driver for high-performance async support
DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

# 2. Create the Database Engine
engine = create_async_engine(DATABASE_URL, echo=True)

# 3. Create the Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 4. Create the Base class for models
Base = declarative_base()


# Dependency to get a DB session in API endpoints
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
