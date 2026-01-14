"""AI Agent main application - FastAPI service for query processing - OPTIMIZED VERSION."""
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
from agent.performance import PerformanceTracker

load_dotenv()

app = FastAPI(
    title="Tarofa AI Agent",
    description="OPTIMIZED scraping and LLM processing agent for Islamic knowledge",
    version="3.0.0"  # Bumped version for optimization release
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
    fuzzy_matched: bool = False


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "tarofa-agent", "version": "3.0.0"}


@app.post("/process", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a search query with OPTIMIZED pipeline.
    
    OPTIMIZATIONS:
    1. Parallel scraping across all sources
    2. Fuzzy cache matching
    3. Scraped data reuse
    4. Reduced LLM context
    5. Intent-based token limits
    """
    perf = PerformanceTracker()
    query = request.query.strip()
    
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    # === STAGE 1: Preprocess query ===
    with perf.track("preprocess"):
        preprocessed = preprocess_query(query)
        intent = preprocessed["intent"]
    
    print(f"\n{'='*50}")
    print(f"[AGENT] Query: '{query[:60]}{'...' if len(query) > 60 else ''}'")
    print(f"[AGENT] Intent: {intent['primary_intent']} (confidence: {intent['confidence']:.2f})")
    
    # === STAGE 2: Check cache (with fuzzy matching) ===
    with perf.track("cache_check"):
        cached_data = cache_manager.get_cached_answer(query)
    
    if cached_data:
        elapsed = perf.get_total_time()
        is_fuzzy = cached_data.get("fuzzy_matched", False)
        print(f"[CACHE {'FUZZY' if is_fuzzy else 'EXACT'}] Returning cached answer in {elapsed:.2f}s")
        perf.print_summary()
        
        return QueryResponse(
            answer=cached_data["answer"],
            sources=cached_data["sources"],
            cached=True,
            intent=intent["primary_intent"],
            processing_time=elapsed,
            fuzzy_matched=is_fuzzy
        )
    
    print(f"[AGENT] Cache miss, processing query...")
    
    try:
        # === STAGE 3: Try to reuse similar scraped data ===
        scraped_articles = None
        
        with perf.track("scraped_cache_check"):
            # First try exact scraped data
            scraped_articles = cache_manager.get_scraped_data(query)
            
            # If not found, try similar scraped data
            if not scraped_articles:
                scraped_articles = cache_manager.get_similar_scraped_data(query)
        
        # === STAGE 4: Scrape if no cached data ===
        if not scraped_articles:
            with perf.track("scraping"):
                scraped_articles = await scraper.scrape_query(query)
        
        if not scraped_articles:
            elapsed = perf.get_total_time()
            answer = build_no_results_response(query)
            perf.print_summary()
            
            return QueryResponse(
                answer=answer,
                sources=[],
                cached=False,
                intent=intent["primary_intent"],
                processing_time=elapsed
            )
        
        # Save scraped data for reuse
        cache_manager.save_scraped_data(query, scraped_articles)
        
        # === STAGE 5: Generate LLM answer ===
        with perf.track("llm_generation"):
            prompt = build_intent_prompt(intent, query, scraped_articles)
            answer = await llm_client.generate(
                SYSTEM_PROMPT, 
                prompt,
                intent=intent["primary_intent"]  # Pass intent for adaptive tokens
            )
        
        # Prepare sources
        sources = [
            {
                "title": a["title"], 
                "url": a["url"], 
                "domain": a["domain"],
                "confidence": a.get("confidence", 0.5),
                "source_type": a.get("source_type", "general_reference")
            }
            for a in scraped_articles[:3]  # Limit to 3 sources
        ]
        
        # Cache the answer
        cache_manager.save_answer(query, answer, sources)
        
        elapsed = perf.get_total_time()
        print(f"\n[AGENT] ✓ Completed in {elapsed:.2f}s")
        perf.print_summary()
        
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
        import traceback
        print(f"[ERROR] Processing failed: {e}")
        print(f"[ERROR] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("AGENT_HOST", "0.0.0.0")
    port = int(os.getenv("AGENT_PORT", "3001"))
    
    print(f"\n{'='*50}")
    print("TAROFA AI AGENT v3.0.0 - OPTIMIZED")
    print(f"{'='*50}")
    print("Optimizations enabled:")
    print("  ✓ Parallel scraping (7 sources simultaneously)")
    print("  ✓ Early termination (3 articles)")
    print("  ✓ Fuzzy cache matching (75% similarity)")
    print("  ✓ Scraped data reuse")
    print("  ✓ Reduced LLM context (6KB vs 20KB)")
    print("  ✓ Adaptive token limits by intent")
    print(f"{'='*50}\n")
    
    uvicorn.run(app, host=host, port=port)
