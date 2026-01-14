"""AI Agent main application - FastAPI service for query processing."""
import os
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from agent.scraper.engine import ScrapingEngine
from agent.llm.client import OpenRouterClient, RateLimitError
from agent.llm.prompts import SYSTEM_PROMPT, build_intent_prompt, build_no_results_response
from agent.cache.manager import CacheManager
from agent.nlp.preprocessor import preprocess_query

load_dotenv()

app = FastAPI(
    title="Tarofa AI Agent",
    description="Scraping and LLM processing agent for Islamic knowledge",
    version="2.0.0"
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
    intent: str = "general"
    processing_time: float = 0.0


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "tarofa-agent", "version": "2.0.0"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a search query with NLP preprocessing.
    
    Pipeline:
    1. Preprocess query (keywords, synonyms, intent)
    2. Check cache
    3. Scrape from approved sources
    4. Generate intent-aware LLM answer
    5. Cache and return result
    """
    start_time = time.time()
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # Preprocess query to get intent
    preprocessed = preprocess_query(query)
    intent = preprocessed["intent"]
    
    print(f"[AGENT] Query: '{query[:50]}...'")
    print(f"[AGENT] Intent: {intent['primary_intent']} (confidence: {intent['confidence']:.2f})")
    
    # Check cache first
    cached_data = cache_manager.get_cached_answer(query)
    if cached_data:
        elapsed = time.time() - start_time
        print(f"[CACHE HIT] Returning cached answer in {elapsed:.2f}s")
        return QueryResponse(
            answer=cached_data["answer"],
            sources=cached_data["sources"],
            cached=True,
            intent=intent["primary_intent"],
            processing_time=elapsed
        )
    
    print(f"[AGENT] Processing new query...")
    
    try:
        # Scrape from approved sources
        scraped_articles = await scraper.scrape_query(query)
        
        if not scraped_articles:
            elapsed = time.time() - start_time
            answer = build_no_results_response(query)
            return QueryResponse(
                answer=answer,
                sources=[],
                cached=False,
                intent=intent["primary_intent"],
                processing_time=elapsed
            )
        
        # Save scraped data
        cache_manager.save_scraped_data(query, scraped_articles)
        
        # Generate intent-aware answer using LLM
        prompt = build_intent_prompt(intent, query, scraped_articles)
        answer = await llm_client.generate(SYSTEM_PROMPT, prompt)
        
        # Prepare sources with confidence and source_type
        sources = [
            {
                "title": a["title"], 
                "url": a["url"], 
                "domain": a["domain"],
                "confidence": a.get("confidence", 0.5),
                "source_type": a.get("source_type", "general_reference")
            }
            for a in scraped_articles
        ]
        
        # Cache the answer
        cache_manager.save_answer(query, answer, sources)
        
        elapsed = time.time() - start_time
        print(f"[AGENT] Completed in {elapsed:.2f}s")
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            cached=False,
            intent=intent["primary_intent"],
            processing_time=elapsed
        )
        
    except RateLimitError as e:
        print(f"[ERROR] Rate limit exceeded: {e}")
        raise HTTPException(
            status_code=429, 
            detail="Layanan sedang sibuk. Silakan coba lagi dalam beberapa saat.",
            headers={"Retry-After": "30"}
        )
    except Exception as e:
        print(f"[ERROR] Processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "3001"))
    
    uvicorn.run(app, host=host, port=port)
