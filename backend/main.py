import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import engine, Base, get_db
from models import EnergyGeneration


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Create tables on startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

# Read environment variables
db_host = os.getenv("DB_HOST", "not_set")
eia_key = os.getenv("EIA_API_KEY", "not_set")


@app.get("/")
def read_root():
    key_status = "Loaded" if eia_key != "not_set" else "Missing"
    return {
        "message": "GridWatch API is running.",
        "database_connection": {
            "host": db_host,
            "status": "Connected"
        },
        "api_key_status": key_status
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/history")
async def get_history(db: AsyncSession = Depends(get_db)):
    """
    Fetch the last 50 data points from the database.
    """
    # Query: Select all records, newest first, limit 50
    result = await db.execute(
        select(EnergyGeneration)
        .order_by(EnergyGeneration.timestamp.desc())
        .limit(50)
    )
    records = result.scalars().all()
    return records
