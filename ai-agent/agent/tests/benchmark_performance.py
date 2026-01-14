"""Performance benchmark test for Tarofai optimization validation."""
import asyncio
import time
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.cache.manager import CacheManager
from agent.scraper.engine import ScrapingEngine
from agent.nlp.preprocessor import preprocess_query


# Test queries
TEST_QUERIES = [
    # Simple queries
    ("hukum zina", "simple"),
    ("sholat tahajud", "simple"),
    
    # Moderate queries
    ("apa hukum musik dalam islam", "moderate"),
    ("cara wudhu yang benar", "moderate"),
    
    # Complex queries
    ("apa hukum dan konsekuensi bagi orang yang meninggalkan sholat wajib", "complex"),
]

TARGET_TIME = 20.0  # Target: < 20 seconds


async def benchmark_scraping():
    """Benchmark scraping performance."""
    print("\n" + "=" * 60)
    print("SCRAPING BENCHMARK")
    print("=" * 60)
    
    scraper = ScrapingEngine()
    
    for query, complexity in TEST_QUERIES[:2]:  # Only test 2 to avoid rate limits
        print(f"\n[TEST] Query: '{query}' ({complexity})")
        
        start = time.time()
        results = await scraper.scrape_query(query)
        elapsed = time.time() - start
        
        status = "✓ PASS" if elapsed < TARGET_TIME else "✗ FAIL"
        print(f"  {status}: {len(results)} articles in {elapsed:.2f}s")
        
        if elapsed >= TARGET_TIME:
            print(f"  WARNING: Exceeded {TARGET_TIME}s target!")


def benchmark_cache():
    """Benchmark cache operations."""
    print("\n" + "=" * 60)
    print("CACHE BENCHMARK")
    print("=" * 60)
    
    cache = CacheManager()
    
    # Test exact match
    test_query = "test benchmark query"
    cache.save_answer(test_query, "Test answer", [{"title": "Test", "url": "http://test.com", "domain": "test.com"}])
    
    start = time.time()
    result = cache.get_cached_answer(test_query)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n[CACHE] Exact match: {elapsed:.2f}ms")
    print(f"  Result: {'Found' if result else 'Not found'}")
    
    # Test fuzzy match
    similar_query = "test benchmark"
    start = time.time()
    result = cache.get_cached_answer(similar_query)
    elapsed = (time.time() - start) * 1000
    
    print(f"\n[CACHE] Fuzzy match: {elapsed:.2f}ms")
    print(f"  Result: {'Found (fuzzy)' if result and result.get('fuzzy_matched') else 'Not found'}")


def benchmark_preprocessing():
    """Benchmark NLP preprocessing."""
    print("\n" + "=" * 60)
    print("PREPROCESSING BENCHMARK")
    print("=" * 60)
    
    for query, complexity in TEST_QUERIES:
        start = time.time()
        result = preprocess_query(query)
        elapsed = (time.time() - start) * 1000
        
        print(f"\n[PREPROCESS] '{query[:40]}...' ({complexity})")
        print(f"  Time: {elapsed:.2f}ms")
        print(f"  Intent: {result['intent']['primary_intent']}")
        print(f"  Keywords: {result['keywords'][:5]}")


async def main():
    """Run all benchmarks."""
    print("\n" + "=" * 60)
    print("TAROFAI PERFORMANCE BENCHMARK")
    print("Target: Response time < 20 seconds")
    print("=" * 60)
    
    benchmark_preprocessing()
    benchmark_cache()
    await benchmark_scraping()
    
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)
    print("\nNote: Full pipeline test requires running the server.")
    print("Start with: python -m agent.main")
    print("Then test with curl or the frontend.")


if __name__ == "__main__":
    asyncio.run(main())
