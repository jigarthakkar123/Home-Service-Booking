from typing import List, Optional, Dict
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, status
from app.services.rag_service import rag_agent, STATIC_OUT_OF_DOMAIN_ANSWER

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class RAGChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []

class RAGChatResponse(BaseModel):
    reply: str
    sources: List[str]
    in_domain: bool
    llm: Optional[str] = None

@router.post("/chat", response_model=RAGChatResponse)
async def chat_with_rag_agent(payload: RAGChatRequest):
    """
    RAG-Powered Chatbot Endpoint.
    Uses 'ragbased.pdf' as authoritative knowledge base.
    If the question cannot be answered from the PDF or is out-of-domain,
    strictly returns the standard static fallback.
    """
    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    result = await rag_agent.answer(payload.message)
    return RAGChatResponse(
        reply=result["reply"],
        sources=result.get("sources", []),
        in_domain=result.get("in_domain", False),
        llm=result.get("llm", "HomeServe Local RAG Engine")
    )

@router.get("/status")
def get_rag_status():
    """
    Health and indexing status for the RAG agent.
    """
    return {
        "status": "online" if rag_agent.pdf_loaded else "indexing_fallback",
        "pdf_loaded": rag_agent.pdf_loaded,
        "total_semantic_chunks": len(rag_agent.chunks),
        "pdf_source": rag_agent.pdf_path or "ragbased.pdf"
    }
