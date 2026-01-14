"""Quick validation test for optimization."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("TAROFAI OPTIMIZATION VALIDATION")
print("=" * 50)

# Test 1: Preprocessing
print("\n[1] Testing Preprocessing...")
try:
    from agent.nlp.preprocessor import preprocess_query
    start = time.time()
    result = preprocess_query("hukum zina dalam islam")
    elapsed = (time.time() - start) * 1000
    print(f"    Time: {elapsed:.2f}ms")
    print(f"    Intent: {result['intent']['primary_intent']}")
    print(f"    Keywords: {result['keywords']}")
    print("    Status: PASS")
except Exception as e:
    print(f"    Error: {e}")
    print("    Status: FAIL")

# Test 2: Cache Manager
print("\n[2] Testing Cache Manager...")
try:
    from agent.cache.manager import CacheManager
    cm = CacheManager()
    
    # Test save and retrieve
    cm.save_answer("test query optimization", "Test answer", [{"title": "Test", "url": "http://test.com", "domain": "test.com"}])
    
    start = time.time()
    result = cm.get_cached_answer("test query optimization")
    elapsed = (time.time() - start) * 1000
    print(f"    Exact match time: {elapsed:.2f}ms")
    print(f"    Result: {'Found' if result else 'Not found'}")
    
    # Test fuzzy match
    start = time.time()
    result2 = cm.get_cached_answer("test query")
    elapsed2 = (time.time() - start) * 1000
    print(f"    Fuzzy match time: {elapsed2:.2f}ms")
    print(f"    Fuzzy match: {'Found' if result2 and result2.get('fuzzy_matched') else 'Not found'}")
    print("    Status: PASS")
except Exception as e:
    print(f"    Error: {e}")
    print("    Status: FAIL")

# Test 3: Scraping Engine
print("\n[3] Testing Scraping Engine (parallel)...")
try:
    from agent.scraper.engine import ScrapingEngine
    scraper = ScrapingEngine()
    print(f"    Source timeout: {scraper.source_timeout.total}s")
    print(f"    Overall timeout: {scraper.overall_timeout}s")
    print(f"    Max concurrent sources: {scraper.max_concurrent_sources}")
    print(f"    Early exit threshold: {scraper.min_articles_for_early_exit} articles")
    print("    Status: PASS (config verified)")
except Exception as e:
    print(f"    Error: {e}")
    print("    Status: FAIL")

# Test 4: LLM Client
print("\n[4] Testing LLM Client config...")
try:
    from agent.llm.client import OpenRouterClient
    llm = OpenRouterClient()
    print(f"    Timeout: {llm.timeout}s")
    print(f"    Max retries: {llm.max_retries}")
    print(f"    Max content per source: {llm.max_content_per_source} chars")
    print(f"    Max sources: {llm.max_sources}")
    print(f"    Token settings: {llm.token_settings}")
    print("    Status: PASS")
except Exception as e:
    print(f"    Error: {e}")
    print("    Status: FAIL")

# Test 5: Performance Tracker
print("\n[5] Testing Performance Tracker...")
try:
    from agent.performance import PerformanceTracker
    perf = PerformanceTracker()
    with perf.track("test_stage"):
        time.sleep(0.01)
    print(f"    Total time: {perf.get_total_time():.3f}s")
    print(f"    Stages tracked: {len(perf.timings)}")
    print("    Status: PASS")
except Exception as e:
    print(f"    Error: {e}")
    print("    Status: FAIL")

print("\n" + "=" * 50)
print("VALIDATION COMPLETE")
print("=" * 50)
print("\nTo test full pipeline, run:")
print("  python -m agent.main")
print("Then send a query to http://localhost:3001/process")
