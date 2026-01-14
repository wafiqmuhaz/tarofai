"""Query cache manager with SMART CACHING - fuzzy matching and scraped data reuse."""
import os
import json
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


class CacheManager:
    """Manages caching with FUZZY MATCHING and scraped data reuse."""
    
    def __init__(self, cache_dir: str = None):
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            # Default to serverData/cache relative to project root
            self.cache_dir = Path(__file__).parent.parent.parent.parent / "serverData" / "cache"
        
        self.scraped_dir = self.cache_dir.parent / "scraped"
        self.keyword_index_path = self.cache_dir / "_keyword_index.json"
        
        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.scraped_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache TTL
        self.answer_ttl_days = 7  # Answers valid for 7 days
        self.scraped_ttl_days = 1  # Scraped data valid for 1 day (fresher)
        
        # Fuzzy matching settings
        self.fuzzy_threshold = 0.75  # 75% keyword overlap for fuzzy match
        
        # Load keyword index
        self._keyword_index = self._load_keyword_index()
    
    def _hash_query(self, query: str) -> str:
        """Generate hash for query string."""
        normalized = query.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()[:16]
    
    def _extract_keywords(self, query: str) -> set[str]:
        """Extract keywords from query for fuzzy matching."""
        # Normalize
        text = query.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove common stop words
        stop_words = {
            "apa", "apakah", "bagaimana", "mengapa", "yang", "dan", "atau",
            "untuk", "dengan", "di", "ke", "dari", "adalah", "ini", "itu",
            "dalam", "pada", "oleh", "akan", "sudah", "bisa", "dapat",
            "saya", "kamu", "dia", "mereka", "kita"
        }
        
        keywords = {
            word for word in text.split() 
            if len(word) > 2 and word not in stop_words
        }
        
        return keywords
    
    def _calculate_similarity(self, keywords1: set[str], keywords2: set[str]) -> float:
        """Calculate Jaccard similarity between keyword sets."""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1 & keywords2)
        union = len(keywords1 | keywords2)
        
        return intersection / union if union > 0 else 0.0
    
    def _load_keyword_index(self) -> dict:
        """Load keyword index from disk."""
        if self.keyword_index_path.exists():
            try:
                with open(self.keyword_index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _save_keyword_index(self):
        """Save keyword index to disk."""
        try:
            with open(self.keyword_index_path, 'w', encoding='utf-8') as f:
                json.dump(self._keyword_index, f, ensure_ascii=False)
        except Exception:
            pass
    
    def _get_cache_path(self, query_hash: str) -> Path:
        """Get cache file path for query hash."""
        return self.cache_dir / f"{query_hash}.json"
    
    def _get_scraped_path(self, query_hash: str) -> Path:
        """Get scraped data file path for query hash."""
        return self.scraped_dir / f"{query_hash}.json"
    
    def _is_expired(self, cached_at: str, ttl_days: int) -> bool:
        """Check if cache entry is expired."""
        if not cached_at:
            return True
        
        try:
            cached_time = datetime.fromisoformat(cached_at)
            return datetime.now() - cached_time > timedelta(days=ttl_days)
        except Exception:
            return True
    
    def _find_fuzzy_match(self, query: str) -> Optional[str]:
        """Find a fuzzy matching cached query."""
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return None
        
        best_match = None
        best_score = 0.0
        
        for cached_hash, cached_info in self._keyword_index.items():
            cached_keywords = set(cached_info.get("keywords", []))
            
            similarity = self._calculate_similarity(query_keywords, cached_keywords)
            
            if similarity > best_score and similarity >= self.fuzzy_threshold:
                # Verify cache file still exists and not expired
                cache_path = self._get_cache_path(cached_hash)
                if cache_path.exists():
                    try:
                        with open(cache_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if not self._is_expired(data.get("cached_at"), self.answer_ttl_days):
                            best_match = cached_hash
                            best_score = similarity
                    except Exception:
                        pass
        
        if best_match:
            print(f"[CACHE] Fuzzy match found (similarity: {best_score:.2f})")
        
        return best_match
    
    def get_cached_answer(self, query: str) -> dict | None:
        """
        Get cached answer with FUZZY MATCHING.
        
        Tries:
        1. Exact hash match
        2. Fuzzy keyword-based match
        """
        # 1. Try exact match first
        query_hash = self._hash_query(query)
        cache_path = self._get_cache_path(query_hash)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                if not self._is_expired(cache_data.get("cached_at"), self.answer_ttl_days):
                    print(f"[CACHE] Exact hit for query hash: {query_hash}")
                    return cache_data
                else:
                    # Remove expired cache
                    cache_path.unlink(missing_ok=True)
            except Exception as e:
                print(f"[CACHE] Error reading cache: {e}")
        
        # 2. Try fuzzy match
        fuzzy_hash = self._find_fuzzy_match(query)
        if fuzzy_hash:
            fuzzy_path = self._get_cache_path(fuzzy_hash)
            try:
                with open(fuzzy_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                # Add note that this is fuzzy matched
                cache_data["fuzzy_matched"] = True
                cache_data["original_query"] = cache_data.get("query", "")
                return cache_data
            except Exception:
                pass
        
        return None
    
    def save_answer(self, query: str, answer: str, sources: list[dict]) -> None:
        """Save answer with keyword indexing for fuzzy matching."""
        query_hash = self._hash_query(query)
        cache_path = self._get_cache_path(query_hash)
        
        keywords = list(self._extract_keywords(query))
        
        cache_data = {
            "query": query,
            "query_hash": query_hash,
            "keywords": keywords,
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
            
            # Update keyword index
            self._keyword_index[query_hash] = {
                "keywords": keywords,
                "cached_at": cache_data["cached_at"]
            }
            self._save_keyword_index()
            
            print(f"[CACHE] Saved answer for query hash: {query_hash}")
        except Exception as e:
            print(f"[CACHE] Error saving cache: {e}")
    
    def save_scraped_data(self, query: str, scraped: list[dict]) -> None:
        """Save raw scraped data for reuse."""
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
        """Get cached scraped data (fresher TTL than answers)."""
        query_hash = self._hash_query(query)
        scraped_path = self._get_scraped_path(query_hash)
        
        if not scraped_path.exists():
            return None
        
        try:
            with open(scraped_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if self._is_expired(data.get("scraped_at"), self.scraped_ttl_days):
                return None
            
            print(f"[CACHE] Using cached scraped data (age: <{self.scraped_ttl_days}d)")
            return data.get("articles", [])
        except Exception as e:
            print(f"[CACHE] Error reading scraped data: {e}")
            return None
    
    def get_similar_scraped_data(self, query: str) -> list[dict] | None:
        """Find scraped data from similar queries using fuzzy matching."""
        query_keywords = self._extract_keywords(query)
        
        if not query_keywords:
            return None
        
        # Scan scraped directory for potential matches
        best_match = None
        best_score = 0.0
        
        for scraped_file in self.scraped_dir.glob("*.json"):
            if scraped_file.name.startswith("_"):
                continue
            
            try:
                with open(scraped_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Check if expired
                if self._is_expired(data.get("scraped_at"), self.scraped_ttl_days):
                    continue
                
                cached_query = data.get("query", "")
                cached_keywords = self._extract_keywords(cached_query)
                
                similarity = self._calculate_similarity(query_keywords, cached_keywords)
                
                if similarity > best_score and similarity >= self.fuzzy_threshold:
                    best_match = data.get("articles", [])
                    best_score = similarity
                    
            except Exception:
                continue
        
        if best_match:
            print(f"[CACHE] Found similar scraped data (similarity: {best_score:.2f})")
        
        return best_match
