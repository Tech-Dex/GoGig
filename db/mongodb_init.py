import logging

from motor.motor_asyncio import AsyncIOMotorClient

from core.config import MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT, MONGODB_URL
from db.mongodb import db


def connect_to_mongo():
    try:
        logging.info("MONGODB: Trying to close the previous connection...")
        db.client.close()
    except Exception:
        logging.warning("MONGODB: The connection was handled before.")
    finally:
        logging.info("MongoDB: Start connection...")
        db.client = AsyncIOMotorClient(
            MONGODB_URL,
            maxPoolSize=MAX_CONNECTIONS_COUNT,
            minPoolSize=MIN_CONNECTIONS_COUNT,
        )
        logging.info("MongoDB: Connection Successful!")


def close_mongo_connection():
    logging.info("MongoDB: Close connection...")
    db.client.close()
    logging.info("MongoDB: Connection closed!")
