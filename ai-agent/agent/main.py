"""AI Agent main application - FastAPI service for query processing."""
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.scraper.engine import ScrapingEngine
from agent.llm.client import OpenRouterClient
from agent.llm.prompts import SYSTEM_PROMPT, build_answer_prompt, build_no_results_response
from agent.cache.manager import CacheManager

load_dotenv()

app = FastAPI(
    title="Tarofa AI Agent",
    description="Scraping and LLM processing agent for Islamic knowledge",
    version="1.0.0"
)

# Initialize components
scraper = ScrapingEngine()
llm_client = OpenRouterClient()
cache_manager = CacheManager()


class QueryRequest(BaseModel):
    """Query request model."""
    query: str


class QueryResponse(BaseModel):
    """Query response model."""
    answer: str
    sources: list[dict]
    cached: bool


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "tarofa-agent"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a search query.
    
    1. Check cache for existing answer
    2. If not cached, scrape from approved sources
    3. Generate answer using LLM
    4. Cache and return result
    """
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Check cache first
    cached_data = cache_manager.get_cached_answer(query)
    if cached_data:
        print(f"[CACHE HIT] Returning cached answer for: {query[:50]}...")
        return QueryResponse(
            answer=cached_data["answer"],
            sources=cached_data["sources"],
            cached=True
        )
    
    print(f"[PROCESSING] New query: {query[:50]}...")
    
    try:
        # Scrape from approved sources
        scraped_articles = await scraper.scrape_query(query)
        
        if not scraped_articles:
            # No results found
            answer = build_no_results_response(query)
            return QueryResponse(
                answer=answer,
                sources=[],
                cached=False
            )
        
        # Save scraped data
        cache_manager.save_scraped_data(query, scraped_articles)
        
        # Generate answer using LLM
        prompt = build_answer_prompt(query, scraped_articles)
        answer = await llm_client.generate(SYSTEM_PROMPT, prompt)
        
        # Prepare sources
        sources = [
            {"title": a["title"], "url": a["url"], "domain": a["domain"]}
            for a in scraped_articles
        ]
        
        # Cache the answer
        cache_manager.save_answer(query, answer, sources)
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            cached=False
        )
        
    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "3001"))
    
    uvicorn.run(app, host=host, port=port)
