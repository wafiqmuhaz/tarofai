"""Async web scraping engine for approved Islamic sources - OPTIMIZED VERSION."""
import asyncio
import re
import time
import aiohttp
from typing import Optional
from urllib.parse import urljoin, urlparse

from .whitelist import is_approved_domain, get_domain, SEARCH_PATTERNS
from .normalizer import extract_article_content


class ScrapingEngine:
    """Async scraping engine with PARALLEL scraping and early termination."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8,ar;q=0.7",
        }
        # OPTIMIZED: Aggressive timeouts
        self.source_timeout = aiohttp.ClientTimeout(total=8)  # 8s per source
        self.article_timeout = aiohttp.ClientTimeout(total=5)  # 5s per article
        self.overall_timeout = 15  # 15s total for all scraping
        
        # Concurrency controls
        self.max_concurrent_sources = 7  # All sources in parallel
        self.max_concurrent_articles = 4  # Limit article fetches
        
        # Early termination
        self.min_articles_for_early_exit = 3  # Stop when we have enough
        
        # Patterns that indicate NON-article pages (to skip)
        self.skip_patterns = [
            r'/page/\d+', r'/category/', r'/tag/', r'/author/', r'/topics/',
            r'/about', r'/contact', r'/profil', r'/tentang', r'/kontak',
            r'/donasi', r'/donate', r'/privacy', r'/terms', r'/disclaimer',
            r'/sitemap', r'/feed', r'/rss',
            r'/login', r'/register', r'/account', r'/user/', r'/member/',
            r'/wp-content/', r'/uploads/', r'\.pdf$', r'\.mp3$', r'\.mp4$',
            r'^/en/?$', r'^/id/?$', r'^/ar/?$',
            r'/search', r'/arsip', r'/archive', r'/buku-tamu', r'/guest',
            r'/info-', r'/jaringan', r'/network', r'/halaman-',
        ]
        
        # Patterns that indicate ARTICLE pages
        self.article_patterns = [
            r'/\d{4}/\d{2}/',
            r'/\d+-[a-z]',
            r'-\d+\.html',
            r'/p/\d+',
            r'/read/',
            r'/artikel/',
            r'/post/',
        ]
    
    async def fetch_page(self, url: str, session: aiohttp.ClientSession, 
                         timeout: aiohttp.ClientTimeout = None) -> Optional[str]:
        """Fetch a single page with timeout."""
        if not is_approved_domain(url):
            return None
        
        try:
            async with session.get(url, headers=self.headers, timeout=timeout or self.source_timeout) as response:
                if response.status == 200:
                    return await response.text()
                return None
        except asyncio.TimeoutError:
            print(f"[TIMEOUT] {get_domain(url)}")
            return None
        except Exception:
            return None
    
    def _is_article_url(self, url: str) -> tuple[bool, float]:
        """Check if URL is likely an article page."""
        path = urlparse(url).path.lower()
        
        for pattern in self.skip_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                return False, 0.0
        
        confidence = 0.5
        for pattern in self.article_patterns:
            if re.search(pattern, path, re.IGNORECASE):
                confidence = 0.9
                break
        
        if len(path) > 30:
            confidence += 0.1
        if '-' in path:
            confidence += 0.1
        if len(path) < 10:
            confidence -= 0.3
        
        return confidence > 0.4, min(confidence, 1.0)
    
    async def extract_article_links(self, search_html: str, base_url: str) -> list[dict]:
        """Extract article links from search results page."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(search_html, 'lxml')
        candidates = []
        seen_urls = set()
        
        # Look for article containers
        article_containers = soup.find_all(['article', 'div'], class_=lambda x: x and any(
            c in str(x).lower() for c in ['post', 'article', 'entry', 'result', 'item', 'search']
        ))
        
        search_areas = article_containers if article_containers else [soup]
        
        for container in search_areas:
            for a in container.find_all('a', href=True):
                href = a['href']
                
                if href.startswith('#') or href.startswith('javascript:'):
                    continue
                
                full_url = urljoin(base_url, href)
                
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                if not is_approved_domain(full_url):
                    continue
                
                is_article, confidence = self._is_article_url(full_url)
                if is_article:
                    link_text = a.get_text(strip=True)
                    if len(link_text) > 20:
                        confidence = min(confidence + 0.1, 1.0)
                    
                    candidates.append({
                        'url': full_url,
                        'confidence': confidence,
                        'link_text': link_text[:100] if link_text else ''
                    })
        
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        return candidates[:3]  # Get top 3 candidates
    
    async def _fetch_article_content(self, candidate: dict, session: aiohttp.ClientSession, 
                                     domain: str, semaphore: asyncio.Semaphore) -> Optional[dict]:
        """Fetch and extract content from a single article."""
        async with semaphore:
            try:
                article_html = await self.fetch_page(
                    candidate['url'], session, timeout=self.article_timeout
                )
                
                if article_html:
                    article_data = extract_article_content(article_html)
                    if article_data["content"] and len(article_data["content"]) > 200:
                        return {
                            "url": candidate['url'],
                            "domain": domain,
                            "title": article_data["title"] or candidate.get('link_text', 'Untitled'),
                            "content": article_data["content"],
                            "excerpt": article_data["excerpt"],
                            "confidence": candidate['confidence'],
                            "source_type": "specific_article" if candidate['confidence'] > 0.7 else "general_reference"
                        }
            except Exception:
                pass
            return None
    
    async def _search_single_source(self, domain: str, search_url: str, 
                                    session: aiohttp.ClientSession,
                                    article_semaphore: asyncio.Semaphore) -> list[dict]:
        """Search a single source and fetch articles - PARALLEL article fetching."""
        results = []
        start = time.time()
        
        try:
            # Fetch search results page
            search_html = await self.fetch_page(search_url, session)
            if not search_html:
                return []
            
            # Extract article links
            article_candidates = await self.extract_article_links(search_html, search_url)
            if not article_candidates:
                return []
            
            # PARALLEL: Fetch all article candidates simultaneously
            tasks = [
                self._fetch_article_content(candidate, session, domain, article_semaphore)
                for candidate in article_candidates[:2]  # Limit to 2 per source
            ]
            
            fetched = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in fetched:
                if isinstance(result, dict) and result:
                    results.append(result)
            
            elapsed = time.time() - start
            if results:
                print(f"[SOURCE] ✓ {domain}: {len(results)} articles in {elapsed:.1f}s")
            
        except asyncio.TimeoutError:
            print(f"[SOURCE] ✗ {domain}: timeout")
        except Exception as e:
            print(f"[SOURCE] ✗ {domain}: {str(e)[:50]}")
        
        return results
    
    async def scrape_query(self, query: str) -> list[dict]:
        """
        Scrape content with PARALLEL scraping across all sources.
        
        OPTIMIZATIONS:
        1. All sources searched in parallel
        2. Articles fetched in parallel with semaphore limiting
        3. Early termination when enough results found
        4. Aggressive timeouts per source
        """
        from agent.nlp.preprocessor import get_optimized_search_queries
        
        start_time = time.time()
        
        # Get search variations (limit to 2 for speed)
        search_variations = get_optimized_search_queries(query)[:2]
        print(f"[SEARCH] Using {len(search_variations)} query variations")
        
        # Use primary query for all sources
        primary_query = search_variations[0] if search_variations else query
        encoded_query = primary_query.replace(" ", "+")
        
        # Build all search URLs
        search_tasks = []
        for domain, pattern in SEARCH_PATTERNS.items():
            search_url = pattern.format(encoded_query)
            search_tasks.append((domain, search_url))
        
        print(f"[SEARCH] Searching {len(search_tasks)} sources in PARALLEL")
        
        all_results = []
        seen_urls = set()
        article_semaphore = asyncio.Semaphore(self.max_concurrent_articles)
        
        # Create connector with limits
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=2)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # PARALLEL: Search all sources simultaneously
            async def search_with_timeout(domain: str, search_url: str):
                try:
                    return await asyncio.wait_for(
                        self._search_single_source(domain, search_url, session, article_semaphore),
                        timeout=self.source_timeout.total
                    )
                except asyncio.TimeoutError:
                    print(f"[SOURCE] ✗ {domain}: overall timeout")
                    return []
            
            tasks = [
                search_with_timeout(domain, url) 
                for domain, url in search_tasks
            ]
            
            # Use asyncio.as_completed for EARLY TERMINATION
            for coro in asyncio.as_completed(tasks, timeout=self.overall_timeout):
                try:
                    results = await coro
                    
                    for result in results:
                        if result['url'] not in seen_urls:
                            seen_urls.add(result['url'])
                            all_results.append(result)
                    
                    # EARLY TERMINATION: Stop when we have enough
                    if len(all_results) >= self.min_articles_for_early_exit:
                        elapsed = time.time() - start_time
                        print(f"[SEARCH] Early exit: {len(all_results)} articles in {elapsed:.1f}s")
                        break
                        
                except asyncio.TimeoutError:
                    print(f"[SEARCH] Source timed out, continuing...")
                except Exception as e:
                    print(f"[SEARCH] Source error: {str(e)[:50]}")
        
        # Sort by confidence
        all_results.sort(key=lambda x: x['confidence'], reverse=True)
        
        elapsed = time.time() - start_time
        print(f"[DONE] Total scraped: {len(all_results)} articles in {elapsed:.1f}s")
        
        return all_results
