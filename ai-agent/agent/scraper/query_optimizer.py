"""Query optimizer for better search results."""
import re


# Indonesian stop words to remove
STOP_WORDS_ID = {
    # Question words
    "apa", "apakah", "bagaimana", "mengapa", "kenapa", "siapa", "kapan", "dimana",
    "berapa", "mana", "bilamana",
    
    # Pronouns
    "saya", "aku", "kamu", "anda", "dia", "ia", "mereka", "kita", "kami",
    
    # Prepositions
    "di", "ke", "dari", "untuk", "dengan", "pada", "oleh", "dalam", "tanpa",
    "kepada", "terhadap", "antara", "hingga", "sampai", "tentang", "mengenai",
    
    # Conjunctions
    "dan", "atau", "tetapi", "tapi", "namun", "serta", "maupun", "melainkan",
    "sedangkan", "padahal", "karena", "sebab", "jika", "bila", "kalau", "maka",
    "supaya", "agar", "bahwa", "ketika", "saat", "setelah", "sebelum",
    
    # Articles and determiners
    "yang", "ini", "itu", "tersebut", "sebuah", "suatu", "sang", "si",
    
    # Auxiliary/Modal
    "adalah", "ialah", "yaitu", "yakni", "merupakan", "bisa", "dapat", "akan",
    "sudah", "telah", "sedang", "masih", "harus", "perlu", "boleh", "tidak",
    "bukan", "belum", "jangan", "tak",
    
    # Common words
    "orang", "hal", "cara", "secara", "sangat", "lebih", "paling", "begitu",
    "seperti", "lagi", "juga", "hanya", "saja", "pun", "lalu", "kemudian",
}

# English stop words
STOP_WORDS_EN = {
    "what", "how", "why", "when", "where", "who", "which", "is", "are", "was",
    "were", "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "must", "shall",
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "into", "through", "during", "before",
    "after", "above", "below", "between", "about", "against", "this", "that",
    "these", "those", "it", "its", "i", "you", "he", "she", "we", "they",
}

ALL_STOP_WORDS = STOP_WORDS_ID | STOP_WORDS_EN


def extract_keywords(query: str) -> list[str]:
    """
    Extract meaningful keywords from query.
    
    Args:
        query: User's search query
        
    Returns:
        List of keywords ordered by importance
    """
    # Normalize
    text = query.lower().strip()
    
    # Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Split into words
    words = text.split()
    
    # Filter stop words and short words
    keywords = [
        word for word in words 
        if word not in ALL_STOP_WORDS and len(word) > 2
    ]
    
    return keywords


def optimize_query(query: str) -> dict:
    """
    Optimize query for better search results.
    
    Returns:
        Dict with:
        - original: Original query
        - keywords: Extracted keywords
        - primary: Main search term
        - variations: Search variations to try
    """
    keywords = extract_keywords(query)
    
    if not keywords:
        # Fallback to original query if no keywords extracted
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 2][:3]
    
    # Primary keyword (usually the most specific/longest)
    keywords_sorted = sorted(keywords, key=len, reverse=True)
    primary = keywords_sorted[0] if keywords_sorted else query
    
    # Build search variations
    variations = []
    
    # 1. Single most important keyword
    if primary:
        variations.append(primary)
    
    # 2. Two keywords combined (if available)
    if len(keywords) >= 2:
        variations.append(f"{keywords[0]} {keywords[1]}")
    
    # 3. Three keywords (if available)
    if len(keywords) >= 3:
        variations.append(" ".join(keywords[:3]))
    
    # 4. All keywords (if short enough)
    if len(keywords) > 3 and len(" ".join(keywords)) < 50:
        variations.append(" ".join(keywords))
    
    return {
        "original": query,
        "keywords": keywords,
        "primary": primary,
        "variations": variations
    }


def get_search_queries(query: str) -> list[str]:
    """
    Get list of search queries to try.
    
    Uses keyword extraction to generate multiple search variations,
    improving chances of finding relevant results.
    
    Args:
        query: User's original query
        
    Returns:
        List of search queries to try (most specific first)
    """
    optimized = optimize_query(query)
    
    # Start with most specific, then broaden
    queries = []
    
    # If original is short (1-2 words), use it directly
    if len(query.split()) <= 2:
        queries.append(query)
    else:
        # For longer queries, use variations
        queries.extend(optimized["variations"])
    
    # Ensure we have at least the primary keyword
    if optimized["primary"] not in queries:
        queries.append(optimized["primary"])
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    return unique_queries[:3]  # Limit to 3 variations max
