from datetime import datetime
from qdrant_client import AsyncQdrantClient, models
from qdrant_client.models import Filter, FieldCondition, DatetimeRange
from ..schemas.qdrant_payload_schema import COLLECTION_PAYLOAD_INDEX_CONFIG
from ..utils.helper import get_index_param
from ..core.logging import get_logger
from typing import List, Dict, Any, Optional

logger = get_logger()

class QdrantService:
    def __init__(self, client: AsyncQdrantClient):
        self.client = client

    async def recreate_collection(self, collection_name: str, vector_size: int, distance_metric: models.Distance = models.Distance.COSINE):
        #This function will deletes the existing collection and creates the new collection
        try:
            await self.client.recreate_collection(
                collection_name=collection_name,
                vectors_config=self.client.get_fastembed_vector_params(),
                sparse_vectors_config=self.client.get_fastembed_sparse_vector_params(on_disk=True)
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
            return True
        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {e}", exc_info=True)
            return False
    
    # async def ingest_data(self, collection_name: str, payload: Dict, documents: list[str], metadata: Optional[list[dict]], ids: Optional[list[int]] = None):
    async def ingest_data(self, collection_name: str, payload: Dict):
        try:
                documents = payload.get('documents')
                metadata = payload.get('metadata')

                await self.client.add(
                    collection_name=collection_name,
                    documents=documents,
                    metadata=metadata
                )
                logger.info(f"Successfully ingested data into collection '{collection_name}'.")
                return True
        except Exception as e:
            logger.error(f"Error ingesting data into collection '{collection_name}': {e}", exc_info=True)
            return False
    
    async def create_collection(
        self,
        collection_name: str,
        **kwargs: Any
    ):
        try:
            colls = await self.client.get_collections()
            if any(c.name == collection_name for c in colls.collections):
                logger.warning(f"Collection '{collection_name}' already exists.")
                return False
            
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config=self.client.get_fastembed_vector_params(),
                sparse_vectors_config=self.client.get_fastembed_sparse_vector_params(on_disk=True),                
            )

            schema = COLLECTION_PAYLOAD_INDEX_CONFIG.get(collection_name)
            if schema:
                for field, field_type in schema.items():
                    await self.client.create_payload_index(
                        collection_name=collection_name,
                        field_name=field,
                        field_schema=get_index_param(field_type)
                    )
            logger.info(f"collection '{collection_name}' created successfully.")
            return True

        except Exception as e:
            logger.error(f"Error creating collection '{collection_name}': {e}", exc_info=True)
            return False
        
    async def upsert_points(self, collection_name: str, points: List[models.PointStruct], wait: bool = True):
        try:
            operation_info = await self.client.upsert(
                collection_name=collection_name,
                wait=wait,
                points=points,
            )
            logger.info(f"Upserted points to '{collection_name}': {operation_info}")
            return operation_info
        except Exception as e:
            logger.error(f"Error upserting points to '{collection_name}': {e}", exc_info=True)
            return None

    async def retrieve_points(self, collection_name: str, ids: List[int], with_payload: bool = True, with_vectors: bool = False):
        try:
            points = await self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            logger.info(f"Retrieved points from '{collection_name}': {len(points)} items.")
            return points
        except Exception as e:
            logger.error(f"Error retrieving points from '{collection_name}': {e}", exc_info=True)
            return []

    async def search_points(self, collection_name: str, query_vector: List[float], limit: int = 10, query_filter: Optional[models.Filter] = None, with_payload: bool = True, with_vectors: bool = False):
        try:
            search_result = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=with_payload,
                with_vectors=with_vectors,
            )
            logger.info(f"Search in '{collection_name}' returned {len(search_result)} results.")
            return search_result
        except Exception as e:
            logger.error(f"Error searching points in '{collection_name}': {e}", exc_info=True)
            return []

    async def delete_points(self, collection_name: str, points_selector: models.PointIdsList | models.Filter, wait: bool = True): # type: ignore
        try:
            operation_info = await self.client.delete(
                collection_name=collection_name,
                points_selector=points_selector,
                wait=wait,
            )
            logger.info(f"Deleted points from '{collection_name}': {operation_info}")
            return operation_info
        except Exception as e:
            logger.error(f"Error deleting points from '{collection_name}': {e}", exc_info=True)
            return None

    async def get_all_collections(self) -> List[str]:
        try:
            collections = await self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]
            logger.info(f"List collections: {collection_names}")
            return collection_names
        except Exception as e:
            logger.error(f"Error listing collections: {e}", exc_info=True)
            return []

    async def delete_collection(self, collection_name: str) -> bool:
        try:
            await self.client.delete_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {e}", exc_info=True)
            return False

    async def search_collection(self, collection_name, query, from_date, to_date):
            try:
                conditions = []
                if from_date or to_date:
                    conditions.append(FieldCondition(
                        key="uploaded_date", 
                        range=DatetimeRange(gte=from_date, lte=to_date)
                    ))
                search_result = await self.client.query(
                                collection_name=collection_name,
                                query_text=query,
                                query_filter=Filter(must=conditions) if conditions else None
                                )
                
                return search_result
            except Exception as e:
                logger.error(f"Error Searching collection '{collection_name}': {e}", exc_info=True)
                return False