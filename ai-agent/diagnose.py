"""Quick diagnostic test for Tarofa agent."""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 50)
print("TAROFA DIAGNOSTIC TEST")
print("=" * 50)

errors = []

# Test 1: Imports
print("\n[1] Testing imports...")
try:
    from agent.nlp.preprocessor import preprocess_query
    print("    ✓ NLP preprocessor OK")
except Exception as e:
    print(f"    ✗ NLP preprocessor FAILED: {e}")
    errors.append(("NLP preprocessor", str(e)))

try:
    from agent.cache.manager import CacheManager
    print("    ✓ Cache manager OK")
except Exception as e:
    print(f"    ✗ Cache manager FAILED: {e}")
    errors.append(("Cache manager", str(e)))

try:
    from agent.scraper.engine import ScrapingEngine
    print("    ✓ Scraping engine OK")
except Exception as e:
    print(f"    ✗ Scraping engine FAILED: {e}")
    errors.append(("Scraping engine", str(e)))

try:
    from agent.llm.client import OpenRouterClient
    print("    ✓ LLM client OK")
except Exception as e:
    print(f"    ✗ LLM client FAILED: {e}")
    errors.append(("LLM client", str(e)))

try:
    from agent.performance import PerformanceTracker
    print("    ✓ Performance tracker OK")
except Exception as e:
    print(f"    ✗ Performance tracker FAILED: {e}")
    errors.append(("Performance tracker", str(e)))

# Test 2: Initialization
print("\n[2] Testing component initialization...")

try:
    cm = CacheManager()
    print("    ✓ CacheManager init OK")
except Exception as e:
    print(f"    ✗ CacheManager init FAILED: {e}")
    errors.append(("CacheManager init", str(e)))

try:
    scraper = ScrapingEngine()
    print("    ✓ ScrapingEngine init OK")
except Exception as e:
    print(f"    ✗ ScrapingEngine init FAILED: {e}")
    errors.append(("ScrapingEngine init", str(e)))

try:
    llm = OpenRouterClient()
    print("    ✓ OpenRouterClient init OK")
    print(f"      Models: {llm.models}")
except Exception as e:
    print(f"    ✗ OpenRouterClient init FAILED: {e}")
    errors.append(("OpenRouterClient init", str(e)))

# Test 3: Simple preprocessing
print("\n[3] Testing preprocessing...")
try:
    result = preprocess_query("hukum zina")
    print(f"    ✓ Preprocessing OK")
    print(f"      Intent: {result['intent']['primary_intent']}")
    print(f"      Keywords: {result['keywords']}")
except Exception as e:
    print(f"    ✗ Preprocessing FAILED: {e}")
    errors.append(("Preprocessing", str(e)))

# Test 4: Quick scraping test
print("\n[4] Testing scraping (async)...")
async def test_scraping():
    try:
        from agent.nlp.preprocessor import get_optimized_search_queries
        queries = get_optimized_search_queries("hukum zina")
        print(f"    ✓ Search queries generated: {queries}")
        return True
    except Exception as e:
        print(f"    ✗ Search query generation FAILED: {e}")
        errors.append(("Search queries", str(e)))
        return False

asyncio.run(test_scraping())

# Summary
print("\n" + "=" * 50)
if errors:
    print(f"DIAGNOSTIC FAILED - {len(errors)} errors found:")
    for name, err in errors:
        print(f"  - {name}: {err}")
else:
    print("DIAGNOSTIC PASSED - All components OK")
print("=" * 50)
