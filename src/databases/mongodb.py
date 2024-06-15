from src.config import settings

from motor.motor_asyncio import AsyncIOMotorClient

# Mongo

# client = AsyncIOMotorClient(settings.MONGO_URL, replicaSet='rs0')
client = AsyncIOMotorClient(settings.MONGO_URL)#, replicaSet='rs0')

db = client[settings.MONGO_NAME]