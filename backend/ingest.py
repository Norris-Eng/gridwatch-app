import asyncio
import os
import httpx
from datetime import datetime, timedelta
from sqlalchemy import select
from database import SessionLocal
from models import EnergyGeneration

# EIA API Endpoint for Electricity Generation (Hourly)
# Request data for the US lower 48 states
EIA_URL = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"


async def fetch_and_store_data():
    """
    Fetches the last 24 hours of energy generation data
    and saves new records to the database.
    """
    api_key = os.getenv("EIA_API_KEY")
    if not api_key or api_key == "not_set":
        print("❌ Error: EIA_API_KEY is missing.")
        return

    print("🚀 Starting data ingestion...")

    # 1. Define the time range (Last 24 hours)
    # EIA data often has a slight lag, so looking back a bit.
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)

    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[0]": "value",
        "start": start_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "end": end_time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 5000
    }

    # 2. Fetch from EIA
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                EIA_URL, params=params, timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ API Request failed: {e}")
            return

    # 3. Process and Save
    if "response" not in data or "data" not in data["response"]:
        print("⚠️ No data found in response.")
        return

    records = data["response"]["data"]
    print(f"📥 Received {len(records)} records. Saving to DB...")

    async with SessionLocal() as session:
        count = 0
        for item in records:
            # Parse fields
            fuel_type = item.get("fueltype")
            value = float(item.get("value", 0))
            ts_str = item.get("period")  # e.g., "2023-10-27T08:00:00"

            # Simple deduplication check:
            # In a real app, I'd use an 'upsert' statement.
            # Here, just check if a record exists for this time + fuel.
            ts = datetime.strptime(ts_str, "%Y-%m-%dT%H")

            stmt = select(EnergyGeneration).where(
                EnergyGeneration.timestamp == ts,
                EnergyGeneration.fuel_type == fuel_type
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if not existing:
                new_record = EnergyGeneration(
                    timestamp=ts,
                    fuel_type=fuel_type,
                    value=value
                )
                session.add(new_record)
                count += 1

        await session.commit()
        print(f"✅ Successfully saved {count} new records.")


if __name__ == "__main__":
    asyncio.run(fetch_and_store_data())
