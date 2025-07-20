from pymongo import AsyncMongoClient
from urllib.parse import quote_plus
from pymongo.server_api import ServerApi
from pymongo.errors import PyMongoError
from fastapi import FastAPI
from ..core.config import get_settings
from ..core.logging import get_logger

logger = get_logger()


async def initialise_mongo(app: FastAPI):
    settings= get_settings()
    username = quote_plus(settings.mongo_username_local)
    password = quote_plus(settings.mongo_password_local)
    database = settings.mongo_database
    uri = f"mongodb://{settings.mongo_host_local}/{database}?retryWrites=true&w=majority"
    mongo_client = AsyncMongoClient(uri, server_api=ServerApi("1"),
                              maxPoolSize=20, minPoolSize=5)
    try:
        await mongo_client.admin.command("ping")
        logger.info("Mongodb Connection Successful")

    except PyMongoError as e:
        logger.error(f"Faile to connect to MongoDB : {e}")
        raise RuntimeError(f"Failed to connect to MongoDB: {e}")
    
    app.state.mongo_client = mongo_client
    app.state.mongo_db = mongo_client[database]
    
    return mongo_client[database]


async def close_mongo_connection(app: FastAPI):
    if hasattr(app.state,'mongo_client') and app.state.mongo_client:
        await app.state.mongo_client.close()
        logger.info("Mongo Connnection Close Sucessfully")