import asyncio
import os
import httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from database import SessionLocal
from models import EnergyGeneration

# EIA API Endpoint for Electricity Generation (Hourly)
EIA_URL = "https://api.eia.gov/v2/electricity/rto/fuel-type-data/data/"


async def fetch_and_store_data():
    """
    Fetches the energy generation data from 24-48 hours ago
    and saves new records to the database.
    """
    api_key = os.getenv("EIA_API_KEY")
    if not api_key or api_key == "not_set":
        print("❌ Error: EIA_API_KEY is missing.")
        return

    print("🚀 Starting data ingestion...")

    # 1. Define the time range
    # EIA data lags. Look at the window from 48h ago to 24h ago
    # to ensure a full, settled set of data.
    end_time = datetime.now(timezone.utc) - timedelta(hours=24)
    start_time = end_time - timedelta(hours=24)

    # 2. Format Params strictly for EIA v2
    # Format MUST be YYYY-MM-DDTHH (No minutes/seconds)
    params = {
        "api_key": api_key,
        "frequency": "hourly",
        "data[]": "value",           # Fixed: Removed index [0]
        "facets[respondent][]": "PJM",
        "start": start_time.strftime("%Y-%m-%dT%H"), # Fixed: Hourly format
        "end": end_time.strftime("%Y-%m-%dT%H"),     # Fixed: Hourly format
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "offset": 0,
        "length": 5000
    }

    # 3. Fetch from EIA
    async with httpx.AsyncClient() as client:
        try:
            # Using string timeout for EIA as it can be slow
            response = await client.get(
                EIA_URL, params=params, timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ API Request failed: {e}")
            # Print response text if available for debugging
            if 'response' in locals():
                print(f"Response: {response.text}")
            return

    # 4. Process and Save
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
            ts_str = item.get("period")

            # Parse string to datetime object
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
