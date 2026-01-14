"""Domain whitelist validator for approved Islamic sources."""
from urllib.parse import urlparse


# Approved Salafi sources only
APPROVED_DOMAINS = [
    # Indonesian Sources
    "konsultasisyariah.com",
    "rumaysho.com",
    "almanhaj.or.id",
    "salafycirebon.com",
    "rodja.tv",
    "radiorodja.com",
    "yufid.com",
    "yufid.tv",
    "muslim.or.id",
    "kajian.net",
    "ngaji.org",
    "islamdownload.net",
    "muslimah.or.id",
    
    # English Sources
    "salafipublications.com",
    "salaf.com",
    "sunnisalafi.com",
    "madeenah.org",
    "aqidah.com",
    "tawhidfirst.com",
    "abovethethrone.com",
    "fiqhonline.com",
    "manhaj.com",
    "piousmuslim.com",
    "islamqa.info",
    
    # Scholar Websites
    "albani.co.uk",
    "binbaz.co.uk",
    "fawzan.co.uk",
    "rabee.co.uk",
    "muqbil.co.uk",
    "ubayd.co.uk",
    "ibntaymiyyah.com",
]


def is_approved_domain(url: str) -> bool:
    """
    Check if URL belongs to an approved domain.
    
    Args:
        url: URL to validate
        
    Returns:
        True if domain is approved, False otherwise
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix if present
        if domain.startswith("www."):
            domain = domain[4:]
        
        return domain in APPROVED_DOMAINS
    except Exception:
        return False


def get_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def get_approved_domains() -> list[str]:
    """Get list of approved domains."""
    return APPROVED_DOMAINS.copy()


def build_search_urls(query: str) -> list[str]:
    """
    Build search URLs for approved sources that support search.
    Uses query optimization for better results with long queries.
    
    Args:
        query: Search query
        
    Returns:
        List of search URLs
    """
    from .query_optimizer import get_search_queries
    
    # Search patterns for sources that support internal search
    search_patterns = {
        # Indonesian
        "konsultasisyariah.com": "https://konsultasisyariah.com/?s={}",
        "rumaysho.com": "https://rumaysho.com/?s={}",
        "almanhaj.or.id": "https://almanhaj.or.id/?s={}",
        "salafycirebon.com": "https://salafycirebon.com/?s={}",
        "muslim.or.id": "https://muslim.or.id/?s={}",
        "muslimah.or.id": "https://muslimah.or.id/?s={}",
        "yufid.com": "https://yufid.com/?s={}",
        "kajian.net": "https://kajian.net/?s={}",
        
        # English
        "islamqa.info": "https://islamqa.info/en/search?q={}",
        "salafipublications.com": "https://www.salafipublications.com/?s={}",
        "madeenah.org": "https://madeenah.org/?s={}",
    }
    
    # Get optimized search queries
    search_queries = get_search_queries(query)
    print(f"[QUERY] Original: '{query}' → Optimized: {search_queries}")
    
    # Use primary optimized query for search
    primary_query = search_queries[0] if search_queries else query
    encoded_query = primary_query.replace(" ", "+")
    
    return [
        pattern.format(encoded_query) 
        for pattern in search_patterns.values()
    ]


# Search patterns (shared between functions)
SEARCH_PATTERNS = {
    # Indonesian (most content)
    "konsultasisyariah.com": "https://konsultasisyariah.com/?s={}",
    "rumaysho.com": "https://rumaysho.com/?s={}",
    "almanhaj.or.id": "https://almanhaj.or.id/?s={}",
    "muslim.or.id": "https://muslim.or.id/?s={}",
    "muslimah.or.id": "https://muslimah.or.id/?s={}",
    "yufid.com": "https://yufid.com/?s={}",
    
    # English
    "islamqa.info": "https://islamqa.info/en/search?q={}",
}


def build_search_urls_multi(query: str) -> dict:
    """
    Build search URLs for a single query variation.
    
    Args:
        query: Search query (already optimized)
        
    Returns:
        Dict with urls and query info
    """
    encoded_query = query.replace(" ", "+")
    
    urls = [
        pattern.format(encoded_query) 
        for pattern in SEARCH_PATTERNS.values()
    ]
    
    return {
        "query": query,
        "encoded": encoded_query,
        "urls": urls
    }
