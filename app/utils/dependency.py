from fastapi import Request, HTTPException, status, Depends
from pymongo.database import Database
from pymongo import AsyncMongoClient
from qdrant_client import AsyncQdrantClient
from ..services.mongo_services import MongoService
from ..services.qdrant_services import QdrantService


def get_mongo_database(request: Request) -> Database:
    return request.app.state.mongo_db

def get_mongo_client(request: Request) -> AsyncMongoClient:
    return request.app.state.mongo_client

def get_gemini_client(request: Request):
    return request.app.state.gemini_client

def get_azureopenai_client(request: Request):
    return request.app.state.azure_openai_client

async def get_qdrant_client(request: Request) -> AsyncQdrantClient:
    if not hasattr(request.app.state, "qdrant_service_client") or not request.app.state.qdrant_service_client:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Qdrant client not initialized")
    return request.app.state.qdrant_service_client

async def get_mongo_service(db: Database = Depends(get_mongo_database)) -> MongoService:
    return MongoService(db)

async def get_qdrant_service(request: Request) -> QdrantService:
    if not hasattr(request.app.state, "qdrant_service_client") or not request.app.state.qdrant_service_client:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Qdrant service not initialized")
    return request.app.state.qdrant_service_client