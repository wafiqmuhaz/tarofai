"""Search API routes."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
