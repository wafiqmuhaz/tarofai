"""Query cache manager for reusing scraped data and answers."""
import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


class CacheManager:
    """Manages caching of queries, scraped data, and answers."""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to serverData/cache relative to project root
            self.cache_dir = Path(__file__).parent.parent.parent.parent / "serverData" / "cache"
        
        self.scraped_dir = self.cache_dir.parent / "scraped"
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scraped_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache TTL (7 days)
        self.ttl_days = 7
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query string."""
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _get_cache_path(self, query_hash: str) -> Path:
        """Get cache file path for query hash."""
        return self.cache_dir / f"{query_hash}.json"
    
    def _get_scraped_path(self, query_hash: str) -> Path:
        """Get scraped data file path for query hash."""
        return self.scraped_dir / f"{query_hash}.json"
    
    def _is_expired(self, cache_data: dict) -> bool:
        """Check if cache entry is expired."""
        cached_at = cache_data.get("cached_at")
        if not cached_at:
            return True
        
        try:
            cached_time = datetime.fromisoformat(cached_at)
            return datetime.now() - cached_time > timedelta(days=self.ttl_days)
        except Exception:
            return True
    
    def get_cached_answer(self, query: str) -> dict | None:
        """
        Get cached answer for query if exists and not expired.
        
        Args:
            query: Search query
            
        Returns:
            Cached data or None
        """
        query_hash = self._hash_query(query)
        cache_path = self._get_cache_path(query_hash)
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            if self._is_expired(cache_data):
                # Remove expired cache
                cache_path.unlink(missing_ok=True)
                return None
            
            return cache_data
        except Exception as e:
            print(f"[CACHE] Error reading cache: {e}")
            return None
    
    def save_answer(self, query: str, answer: str, sources: list[dict]) -> None:
        """
        Save answer and sources to cache.
        
        Args:
            query: Original query
            answer: Generated answer
            sources: List of source references
        """
        query_hash = self._hash_query(query)
        cache_path = self._get_cache_path(query_hash)
        
        cache_data = {
            "query": query,
            "query_hash": query_hash,
            "answer": answer,
            "sources": [
                {"title": s.get("title", ""), "url": s.get("url", ""), "domain": s.get("domain", "")}
                for s in sources
            ],
            "cached_at": datetime.now().isoformat()
        }
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            print(f"[CACHE] Saved answer for query hash: {query_hash}")
        except Exception as e:
            print(f"[CACHE] Error saving cache: {e}")
    
    def save_scraped_data(self, query: str, scraped: list[dict]) -> None:
        """
        Save raw scraped data for a query.
        
        Args:
            query: Original query
            scraped: List of scraped article data
        """
        query_hash = self._hash_query(query)
        scraped_path = self._get_scraped_path(query_hash)
        
        scraped_data = {
            "query": query,
            "query_hash": query_hash,
            "scraped_at": datetime.now().isoformat(),
            "articles": scraped
        }
        
        try:
            with open(scraped_path, 'w', encoding='utf-8') as f:
                json.dump(scraped_data, f, ensure_ascii=False, indent=2)
            print(f"[CACHE] Saved scraped data for query hash: {query_hash}")
        except Exception as e:
            print(f"[CACHE] Error saving scraped data: {e}")
    
    def get_scraped_data(self, query: str) -> list[dict] | None:
        """
        Get cached scraped data for query.
        
        Args:
            query: Search query
            
        Returns:
            List of scraped articles or None
        """
        query_hash = self._hash_query(query)
        scraped_path = self._get_scraped_path(query_hash)
        
        if not scraped_path.exists():
            return None
        
        try:
            with open(scraped_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if data is from last TTL period
            scraped_at = data.get("scraped_at")
            if scraped_at:
                scraped_time = datetime.fromisoformat(scraped_at)
                if datetime.now() - scraped_time > timedelta(days=self.ttl_days):
                    return None
            
            return data.get("articles", [])
        except Exception as e:
            print(f"[CACHE] Error reading scraped data: {e}")
            return None
