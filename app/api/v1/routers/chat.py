from fastapi import APIRouter
from ....schemas.chat_validation import ChatRequest


router = APIRouter()

@router.post("/chat")
async def chat_endpoint(user_query : ChatRequest):
    pass