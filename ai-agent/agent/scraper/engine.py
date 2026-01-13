"""Async web scraping engine for approved Islamic sources."""
import asyncio
import aiohttp
from typing import Optional
from urllib.parse import urljoin, urlparse

from .whitelist import is_approved_domain, get_domain, build_search_urls
from .normalizer import extract_article_content


class ScrapingEngine:
    """Async scraping engine for approved sources only."""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
        }
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.rate_limit_delay = 1.0  # Seconds between requests to same domain
    
    async def fetch_page(self, url: str, session: aiohttp.ClientSession) -> Optional[str]:
        """
        Fetch a single page.
        
        Args:
            url: URL to fetch
            session: aiohttp session
            
        Returns:
            HTML content or None if failed
        """
        if not is_approved_domain(url):
            print(f"[BLOCKED] Domain not approved: {url}")
            return None
        
        try:
            async with session.get(url, headers=self.headers) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"[ERROR] HTTP {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            print(f"[TIMEOUT] Request timed out: {url}")
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return None
    
    async def extract_article_links(self, search_html: str, base_url: str) -> list[str]:
        """
        Extract article links from search results page.
        
        Args:
            search_html: HTML of search results
            base_url: Base URL for resolving relative links
            
        Returns:
            List of article URLs
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(search_html, 'lxml')
        links = []
        
        # Find article links - common patterns
        for a in soup.find_all('a', href=True):
            href = a['href']
            
            # Skip navigation, pagination, category links
            skip_patterns = ['page/', 'category/', 'tag/', 'author/', '#', 'javascript:']
            if any(pattern in href.lower() for pattern in skip_patterns):
                continue
            
            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            
            # Only include approved domains
            if is_approved_domain(full_url) and full_url not in links:
                # Check if it looks like an article URL (has path beyond domain)
                parsed = urlparse(full_url)
                if len(parsed.path) > 1 and parsed.path != '/':
                    links.append(full_url)
        
        # Limit to top results
        return links[:5]
    
    async def scrape_query(self, query: str) -> list[dict]:
        """
        Scrape content for a query from all approved sources.
        
        Args:
            query: Search query
            
        Returns:
            List of scraped articles with content
        """
        results = []
        search_urls = build_search_urls(query)
        
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            # Fetch search results from all sources
            for search_url in search_urls:
                domain = get_domain(search_url)
                print(f"[SEARCH] Searching {domain}...")
                
                search_html = await self.fetch_page(search_url, session)
                if not search_html:
                    continue
                
                # Extract article links
                article_links = await self.extract_article_links(search_html, search_url)
                
                # Fetch each article
                for article_url in article_links[:3]:  # Limit per source
                    await asyncio.sleep(self.rate_limit_delay)
                    
                    print(f"[FETCH] Fetching article: {article_url}")
                    article_html = await self.fetch_page(article_url, session)
                    
                    if article_html:
                        article_data = extract_article_content(article_html)
                        if article_data["content"]:
                            results.append({
                                "url": article_url,
                                "domain": domain,
                                "title": article_data["title"],
                                "content": article_data["content"],
                                "excerpt": article_data["excerpt"]
                            })
        
        print(f"[DONE] Scraped {len(results)} articles")
        return results
