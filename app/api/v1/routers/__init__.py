from fastapi import APIRouter
from . import _mongo,_qdrant,file_upload,chat

router = APIRouter()


router.include_router(_mongo.router)
router.include_router(_qdrant.router)
router.include_router(file_upload.router)
router.include_router(chat.router)