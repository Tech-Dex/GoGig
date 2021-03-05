from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient = None


db = Database()


def get_database() -> AsyncIOMotorClient:
    return db.client
