from fastapi import APIRouter, HTTPException
from app.models.chat_models import (
    ChatRequest,
    ChatResponse
)
from app.services.ai_service import process_message

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    try:

        result = await process_message(
            request.message
        )

        return ChatResponse(
            success=True,
            reply=result["reply"]
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )