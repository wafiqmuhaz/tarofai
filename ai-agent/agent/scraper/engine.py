"""Async web scraping engine for approved Islamic sources."""
import asyncio
import re
import aiohttp
from typing import Optional
from urllib.parse import urljoin, urlparse

from .whitelist import is_approved_domain, get_domain, build_search_urls_multi
from .normalizer import extract_article_content


class ScrapingEngine:
    """Async scraping engine with multi-query fallback strategy."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8,ar;q=0.7",
        }
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.rate_limit_delay = 0.3
        
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
    
    async def fetch_page(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """Fetch a single page."""
        if not is_approved_domain(url):
            return None
        
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
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
        return candidates[:5]
    
    async def _search_single_query(self, query: str, session: aiohttp.ClientSession) -> list[dict]:
        """Search with a single query variation."""
        results = []
        search_data = build_search_urls_multi(query)
        
        for search_url in search_data['urls']:
            domain = get_domain(search_url)
            
            search_html = await self.fetch_page(search_url, session)
            if not search_html:
                continue
            
            article_candidates = await self.extract_article_links(search_html, search_url)
            
            if not article_candidates:
                continue
            
            for candidate in article_candidates[:2]:
                await asyncio.sleep(self.rate_limit_delay)
                
                article_url = candidate['url']
                confidence = candidate['confidence']
                
                article_html = await self.fetch_page(article_url, session)
                
                if article_html:
                    article_data = extract_article_content(article_html)
                    if article_data["content"] and len(article_data["content"]) > 200:
                        results.append({
                            "url": article_url,
                            "domain": domain,
                            "title": article_data["title"] or candidate.get('link_text', 'Untitled'),
                            "content": article_data["content"],
                            "excerpt": article_data["excerpt"],
                            "confidence": confidence,
                            "source_type": "specific_article" if confidence > 0.7 else "general_reference"
                        })
        
        return results
    
    async def scrape_query(self, query: str) -> list[dict]:
        """
        Scrape content with multi-query fallback strategy.
        
        Strategy:
        1. Use NLP preprocessor to extract keywords and synonyms
        2. Try multiple search variations
        3. Combine and deduplicate results
        """
        from agent.nlp.preprocessor import get_optimized_search_queries
        
        search_variations = get_optimized_search_queries(query)
        print(f"[SEARCH] Will try {len(search_variations)} variations")
        
        all_results = []
        seen_urls = set()
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            for variation in search_variations:
                print(f"[SEARCH] Trying variation: '{variation}'")
                
                results = await self._search_single_query(variation, session)
                
                # Add unique results
                for result in results:
                    if result['url'] not in seen_urls:
                        seen_urls.add(result['url'])
                        all_results.append(result)
                
                # If we have enough results, stop
                if len(all_results) >= 6:
                    print(f"[SEARCH] Found enough results, stopping early")
                    break
                
                # Small delay between variations
                if len(all_results) == 0:
                    await asyncio.sleep(0.5)
        
        # Sort by confidence
        all_results.sort(key=lambda x: x['confidence'], reverse=True)
        print(f"[DONE] Total scraped: {len(all_results)} articles")
        
        return all_results
