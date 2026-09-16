from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from agent.langchain_agent import get_agent_response_stream

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    google_credentials: Optional[Dict[str, Any]] = None
    mode: str = "normal"

# We no longer need ChatResponse because we are streaming via SSE.
# Kept for backward compatibility if other routes imported it, but /chat won't use it.

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # Return a StreamingResponse that consumes the async generator
    return StreamingResponse(
        get_agent_response_stream(request.query, request.history, request.google_credentials, request.mode),
        media_type="text/event-stream"
    )
