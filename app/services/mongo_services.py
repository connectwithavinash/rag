from pymongo.database import Database
from pymongo.collection import Collection
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError, DuplicateKeyError, CollectionInvalid
from ..core.logging import get_logger
from typing import Dict, Any

logger = get_logger()

class MongoService:
    def __init__(self, db: Database):
        self.db = db

    async def create_collection_if_not_exists(self, collection_name: str) -> tuple[Collection, bool]:
        try:
            existing_collections = await self.db.list_collection_names()
            if collection_name in existing_collections:
                logger.info(f"Collection '{collection_name}' already exists.")
                return self.db[collection_name], False
            
            await self.db.create_collection(collection_name)
            logger.info(f"Collection '{collection_name}' created.")
            return self.db[collection_name], True
    
        except CollectionInvalid as e:
            logger.error(f"Invalid collection name: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid collection name: {collection_name}"
            )
    
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A document with the same key already exists."
            )

        except PyMongoError as e:
            logger.exception(f"MongoDB error while creating collection: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal database error"
            )
            
    async def insert_document(self, collection_name: str, document: dict) -> Dict[str, Any]:
        try:
            result = await self.db[collection_name].insert_one(document)
            logger.info(f"Inserted document into '{collection_name}' with ID: {result.inserted_id}")
            return str(result.inserted_id)

        except DuplicateKeyError as e:
            logger.warning(f"Duplicate key error: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Document with duplicate key already exists."
            )
        except PyMongoError as e:
            logger.exception(f"MongoDB insert error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert document."
            )

    async def update_document(self, collection_name: str, filter: dict, update_data: dict) -> Dict[str, Any]:
        try:
            result = await self.db[collection_name].update_one(filter, {"$set": update_data})
            if result.matched_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found for update."
                )
            logger.info(f"Updated document in '{collection_name}', matched: {result.matched_count}")
            return {"updated_count": result.modified_count}

        except PyMongoError as e:
            logger.exception(f"MongoDB update error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update document."
            )
        
    async def delete_document(self, collection_name: str, filter: dict) -> Dict[str, Any]:
        try:
            result = await self.db[collection_name].delete_one(filter)
            if result.deleted_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Document not found for deletion."
                )
            logger.info(f"Deleted document from '{collection_name}', count: {result.deleted_count}")
            return {"deleted_count": result.deleted_count}

        except PyMongoError as e:
            logger.exception(f"MongoDB delete error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete document."
            )