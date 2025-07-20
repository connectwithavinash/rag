from fastapi import APIRouter, Depends, Body, HTTPException
from qdrant_client import models
from typing import List, Optional
from ....services.qdrant_services import QdrantService
from ....utils.dependency import get_qdrant_service
from ....schemas.qdrant_validations import Ingestdata, SearchRequest
from ....core.logging import get_logger

logger = get_logger()
router = APIRouter()


@router.post("/qdrant/create_collection")
async def create_qdrant_collection(
    collection_name: str,
    qdrant_service_client: QdrantService = Depends(get_qdrant_service)
):
    success = await qdrant_service_client.create_collection(
        collection_name=collection_name
    )
    if success:
        return {
            "message": f"Qdrant hybrid collection '{collection_name}' created successfully.",
            "status": "success"
        }
    else:
        return {
            "message": f"Failed to create Qdrant hybrid collection '{collection_name}'.",
            "status": "failure"
        }


@router.post("/qdrant/upsert_points")
async def upsert_qdrant_points(
    collection_name: str,
    points: List[models.PointStruct] = Body(...),
    qdrant_client: QdrantService = Depends(get_qdrant_service)
):
    operation_info = await qdrant_client.upsert_points(collection_name, points)
    if operation_info:
        return {"message": f"Points upserted to '{collection_name}' successfully.", "status": "success", "operation_info": operation_info}
    else:
        return {"message": f"Failed to upsert points to '{collection_name}'.", "status": "failure"}


@router.get("/qdrant/retrieve_points")
async def retrieve_qdrant_points(
    collection_name: str,
    ids: List[int],
    with_payload: bool = True,
    with_vectors: bool = False,
    qdrant_client: QdrantService = Depends(get_qdrant_service)
):
    points = await qdrant_client.retrieve_points(collection_name, ids, with_payload, with_vectors)
    if points:
        return {"message": f"Points retrieved from '{collection_name}' successfully.", "status": "success", "points": points}
    else:
        return {"message": f"Failed to retrieve points from '{collection_name}'.", "status": "failure"}


@router.post("/qdrant/search_points")
async def search_qdrant_points(
    collection_name: str,
    query_vector: List[float] = Body(...),
    limit: int = 10,
    query_filter: Optional[models.Filter] = None,
    with_payload: bool = True,
    with_vectors: bool = False,
    qdrant_client: QdrantService = Depends(get_qdrant_service)
):
    search_result = await qdrant_client.search_points(collection_name, query_vector, limit, query_filter, with_payload, with_vectors)
    if search_result:
        return {"message": f"Search in '{collection_name}' returned results successfully.", "status": "success", "result": search_result}
    else:
        return {"message": f"Failed to search points in '{collection_name}'.", "status": "failure"}


@router.post("/qdrant/delete_points")
async def delete_qdrant_points(
    collection_name: str,
    points_selector: models.PointIdsList | models.Filter = Body(...), # type: ignore
    qdrant_client: QdrantService = Depends(get_qdrant_service)
):
    operation_info = await qdrant_client.delete_points(collection_name, points_selector)

@router.get("/qdrant/list_collections")
async def list_qdrant_collections(
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    collection_names = await qdrant_service.get_all_collections()
    if collection_names:
        return {"message": "Collections retrieved successfully.", "status": "success", "collections": collection_names}
    else:
        return {"message": "Failed to retrieve collections.", "status": "failure"}

@router.post("/qdrant/delete_collection")
async def delete_qdrant_collection(
    collection_name: str,
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    success = await qdrant_service.delete_collection(collection_name)
    if success:
        return {"message": f"Collection '{collection_name}' deleted successfully.", "status": "success"}
    else:
        return {"message": f"Failed to delete collection '{collection_name}'.", "status": "failure"}


# @router.post("/qdrant/ingest_data")
async def ingest_qdrant_data(body : Ingestdata,
    qdrant_service: QdrantService = Depends(get_qdrant_service)
):
    try:
        collection_name = body.collection_name
        qdrant_payload = {
            "documents" : body.documents,
            "metadata " : body.metadata
        }
        success = await qdrant_service.ingest_data(collection_name, qdrant_payload)
        return {"message": f"Data ingested successfully into collection '{collection_name}'.", "status": "success"}
    except Exception as e:
        logger.error(f"Failed to ingest data into collection '{collection_name}'. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest data into collection '{collection_name}'. Error: {e}")

@router.post("/qdrant/search")
async def search(body: SearchRequest,
            qdrant_service_client: QdrantService = Depends(get_qdrant_service)):
    try:
        collection_name = body.collection_name
        query = body.query
        from_date = body.from_date
        to_date = body.to_date
        
        search_response = await qdrant_service_client.search_collection(collection_name, query, from_date, to_date)
        if search_response:
            return {
                    "Results":search_response ,
                    "status": "success"
                }
        else:
            return {
                    "message": f"Failed to Qdrant hybrid collection '{collection_name}'.",
                    "status": "failure"
                }
        
        
    except Exception as e:
        logger.error(f"Failed to fetch records from '{collection_name}'. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch records from '{collection_name}'. Error: {e}")