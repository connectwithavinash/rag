from fastapi import APIRouter, Depends
from ....services.mongo_services import MongoService
from ....utils.dependency import get_mongo_service, get_mongo_service
from ....schemas.common import SuccessResponse

router = APIRouter()


@router.post('/mongo/create_collection', response_model=SuccessResponse)
async def create_new_collection(collection_name: str, mongo_service: MongoService = Depends(get_mongo_service)):
        collection, created = await mongo_service.create_collection_if_not_exists(collection_name)
        message = f"Collection '{collection_name}' is ready."
        if created:
            message = f"Collection '{collection_name}' created successfully."
        else:
            message = f"Collection '{collection_name}' already exists."
        return SuccessResponse(
            message=message,
            data={
                "collection": collection.name,
                "created": created
            }
        )

@router.post("/mongo/create_document", response_model=SuccessResponse)
async def insert_data(collection_name: str, document: dict, mongo_service: MongoService = Depends(get_mongo_service)):
    result = await mongo_service.insert_document(collection_name, document)
    return SuccessResponse(
        message="Document inserted successfully.",
        data=result
    )

@router.put("/mongo/update_document", response_model=SuccessResponse)
async def update_data(collection_name: str, filter: dict, update_data: dict, mongo_service: MongoService = Depends(get_mongo_service)):
    result = await mongo_service.update_document(collection_name, filter, update_data)
    return SuccessResponse(
        message="Document updated successfully.",
        data=result
    )

@router.delete("/mongo/delete_document", response_model=SuccessResponse)
async def delete_data(collection_name: str, filter: dict, mongo_service: MongoService = Depends(get_mongo_service)):
    result = await mongo_service.delete_document(collection_name, filter)
    return SuccessResponse(
        message="Document deleted successfully.",
        data=result
    )


