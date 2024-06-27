from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings


# client = AsyncIOMotorClient(settings.MONGO_URL, replicaSet='rs0')
client = AsyncIOMotorClient(settings.MONGO_URL)

db = client[settings.MONGO_NAME]
