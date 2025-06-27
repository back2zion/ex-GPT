"""채팅 관련 API 엔드포인트"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    sources: List[str]

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """채팅 API"""
    return ChatResponse(
        response=f"'{request.message}'에 대한 답변입니다.",
        conversation_id="conv_001",
        sources=["document1.pdf"]
    )
