import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events: Code to run before the app starts
    and after it shuts down.
    """
    # 1. Create Database Tables
    # This connects to the DB and creates tables defined in models.py
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield
    # (Shutdown code could go here)


app = FastAPI(lifespan=lifespan)

# Read environment variables
db_host = os.getenv("DB_HOST", "not_set")
eia_key = os.getenv("EIA_API_KEY", "not_set")


@app.get("/")
def read_root():
    """
    Root endpoint.
    """
    # Hide the actual key in response, just show if it's loaded
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
