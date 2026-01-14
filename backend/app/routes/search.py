"""Search API routes."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

from app.services.agent_client import AgentClient

router = APIRouter()
agent_client = AgentClient()


class SearchRequest(BaseModel):
    """Search request model."""
    query: str
    

class SourceReference(BaseModel):
    """Source reference in response."""
    title: str
    url: str
    domain: str


class SearchResponse(BaseModel):
    """Search response model."""
    query: str
    answer: str
    sources: list[SourceReference]
    cached: bool


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Search for Islamic knowledge.
    
    - Sends query to AI agent
    - Agent scrapes approved sources
    - LLM generates summarized answer
    - Returns answer with source citations
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = await agent_client.search(request.query)
        return SearchResponse(
            query=request.query,
            answer=result.get("answer", ""),
            sources=[
                SourceReference(
                    title=s.get("title", ""),
                    url=s.get("url", ""),
                    domain=s.get("domain", "")
                )
                for s in result.get("sources", [])
            ],
            cached=result.get("cached", False)
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            raise HTTPException(
                status_code=429, 
                detail="Layanan sedang sibuk. Silakan coba lagi dalam beberapa saat.",
                headers={"Retry-After": "30"}
            )
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.post("/search-stream")
async def search_stream(request: SearchRequest):
    """
    Search for Islamic knowledge with STREAMING response.
    
    Returns Server-Sent Events (SSE) that are proxied from the AI Agent.
    Events include:
    - status: Processing stage updates
    - token: Individual LLM output tokens
    - sources: Source references
    - done: Completion signal
    - error: Error message
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    async def stream_generator():
        """Forward SSE events from AI Agent."""
        try:
            async for event in agent_client.search_stream(request.query):
                yield event
        except httpx.HTTPStatusError as e:
            import json
            if e.response.status_code == 429:
                yield f"event: error\ndata: {json.dumps({'message': 'Layanan sedang sibuk. Silakan coba lagi.'})}\n\n"
            else:
                yield f"event: error\ndata: {json.dumps({'message': f'Search failed: {str(e)}'})}\n\n"
        except Exception as e:
            import json
            yield f"event: error\ndata: {json.dumps({'message': f'Terjadi kesalahan: {str(e)}'})}\n\n"
    
    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
