from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.exceptions import HTTPException
from ....constants import MAX_FILE_SIZE
from ....utils.helper import validate_file_type, validate_file_size
from ....services.process_documents import extract_details
from ....prompts.prompts_manager import PromptManager, get_prompt_manager
from ....utils.dependency import get_gemini_client, get_mongo_service, get_qdrant_service
from ....core.logging import get_logger
from ....services.mongo_services import MongoService
from ....providers.llm.gemini import GeminiClient
from ....services.qdrant_services import QdrantService
from ....schemas.common import SuccessResponse

router = APIRouter()
logger = get_logger()

@router.post("/upload", response_model=SuccessResponse)
async def upload_file(
    collection_name: str = Form(...),
    file: UploadFile = File(...),
    prompt_manager: PromptManager = Depends(get_prompt_manager),
    gemini_client: GeminiClient = Depends(get_gemini_client),
    mongo_service: MongoService = Depends(get_mongo_service),
    qdrant_service : QdrantService = Depends(get_qdrant_service),
    page_by_page: Optional[bool] = True
):
    inserted_id = None
    current_datetime = datetime.now(timezone.utc)

    try:
        file_content = await file.read()
        file_size = len(file_content)

        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=413,
                detail=f"File size ({file_size / (1024*1024):.2f}MB) exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB"
            )

        if not validate_file_type(file_content, file.filename):
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Only PDF and JPEG files are allowed."
            )

        processed_content = None
        if file.content_type == "application/pdf":
            processed_content = await extract_details(collection_name, file_content, prompt_manager, gemini_client)

        elif file.content_type in ['image/jpeg', 'image/jpg']:
            # For images, extract_details expects bytes content, not UploadFile object
            processed_content = await extract_details(collection_name, file_content, prompt_manager, gemini_client)

        if processed_content:
            mongo_payload = {
                "document": processed_content,
                "uploaded_date": current_datetime,
                "filename":file.filename
            }

            try:
                inserted_id = await mongo_service.insert_document(collection_name, mongo_payload)
            
            except Exception as e:
                logger.error(f"Exception Occurred During MongoDB insertion operation: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail="Failed to save processed document to database."
                )
            
            if inserted_id:
                qdrant_payload = {
                    "documents": [processed_content],
                    "metadata": [{"uploaded_date" :current_datetime,
                        "filename": file.filename,
                        "document_id":inserted_id}]
                    }                
            try:
                status = await qdrant_service.ingest_data(collection_name, qdrant_payload)

                if status:
                    return SuccessResponse(
                        message="File uploaded successfully",
                        data={
                            "collection_name": collection_name,
                            "filename": file.filename,
                            "file_size": f"{file_size / (1024*1024):.2f}MB",
                            "content_type": file.content_type
                        }
                    )
            except Exception as qdrant_error:
                try:
                    await mongo_service.delete_document(collection_name, inserted_id)
                except Exception as mongo_error:
                    raise HTTPException(
                        status_code=500,
                        detail = f"MongoDB insertion rolled back. Error"
                    )
                logger.error(f"Qdrant insertion failed. Rolling back MongoDB insertion with id: {inserted_id}. Error: {qdrant_error}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to ingest data into Qdrant. MongoDB insertion rolled back. Error: {qdrant_error}"
                )                    
        else:
            logger.error("No content processed or document not inserted.")
            raise HTTPException(
                status_code=500,
                detail="File processed but document could not be inserted."
            )
        
    except Exception as e:
        logger.error(f"An unexpected error occurred during file upload: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while processing the file: {str(e)}"
        )