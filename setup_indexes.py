import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


async def create_indexes() -> None:
    mongo_uri = os.getenv("MONGO_URI")
    database_name = os.getenv("DATABASE_NAME")

    if not mongo_uri or not database_name:
        raise ValueError("MONGO_URI and DATABASE_NAME must be set in backend/.env")

    client = AsyncIOMotorClient(mongo_uri)
    db = client[database_name]

    await db["users"].create_index("email", unique=True)
    await db["scans"].create_index("user_id")
    await db["scans"].create_index([("user_id", 1), ("scanned_at", -1)])

    print("Indexes created successfully.")
    client.close()


if __name__ == "__main__":
    asyncio.run(create_indexes())
