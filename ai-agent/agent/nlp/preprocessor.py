"""Query preprocessor combining all NLP enhancements."""
import re
from typing import Optional

from .synonyms import expand_query_synonyms, get_related_terms, get_synonyms
from .intent import detect_intent, get_intent_search_boost


# Indonesian stop words (comprehensive)
STOP_WORDS = {
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
    # Articles
    "yang", "ini", "itu", "tersebut", "sebuah", "suatu", "sang", "si",
    # Auxiliary
    "adalah", "ialah", "yaitu", "yakni", "merupakan", "bisa", "dapat", "akan",
    "sudah", "telah", "sedang", "masih", "harus", "perlu", "boleh", "tidak",
    "bukan", "belum", "jangan", "tak",
    # Common fillers
    "orang", "hal", "cara", "secara", "sangat", "lebih", "paling", "begitu",
    "seperti", "lagi", "juga", "hanya", "saja", "pun", "lalu", "kemudian",
    "tolong", "mohon", "coba", "dong", "sih", "nih", "ya", "lah",
}


def simple_stem(word: str) -> str:
    """
    Simple Indonesian stemmer without external dependencies.
    Removes common prefixes and suffixes.
    """
    word = word.lower()
    
    # Common prefixes
    prefixes = ["meng", "mem", "men", "me", "peng", "pem", "pen", "pe", 
                "ber", "be", "di", "ter", "ke", "se"]
    
    # Common suffixes
    suffixes = ["kan", "an", "i", "nya", "lah", "kah"]
    
    # Remove prefixes
    for prefix in prefixes:
        if word.startswith(prefix) and len(word) > len(prefix) + 2:
            word = word[len(prefix):]
            break
    
    # Remove suffixes
    for suffix in suffixes:
        if word.endswith(suffix) and len(word) > len(suffix) + 2:
            word = word[:-len(suffix)]
            break
    
    return word


def extract_keywords(query: str) -> list[str]:
    """Extract meaningful keywords from query."""
    # Normalize
    text = query.lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)
    
    words = text.split()
    
    # Filter stop words and short words
    keywords = [
        word for word in words 
        if word not in STOP_WORDS and len(word) > 2
    ]
    
    return keywords


def preprocess_query(query: str) -> dict:
    """
    Full query preprocessing pipeline.
    
    Args:
        query: Raw user query
        
    Returns:
        Dict with:
        - original: Original query
        - keywords: Extracted keywords
        - stemmed: Stemmed keywords
        - expanded: Synonym-expanded keywords
        - intent: Detected intent
        - search_queries: Optimized search queries to try
    """
    # Extract keywords
    keywords = extract_keywords(query)
    
    # Stem keywords
    stemmed = [simple_stem(k) for k in keywords]
    stemmed = list(set(stemmed))  # Remove duplicates
    
    # Expand with synonyms
    expanded = expand_query_synonyms(keywords)
    
    # Detect intent
    intent = detect_intent(query)
    
    # Get intent-based boost terms
    intent_boost = get_intent_search_boost(intent["primary_intent"])
    
    # Build search queries (most specific to broadest)
    search_queries = []
    
    # 1. Combined keywords (most specific)
    if len(keywords) >= 2:
        search_queries.append(" ".join(keywords[:3]))
    
    # 2. Primary keyword with intent boost
    if keywords and intent_boost:
        primary = keywords[0]
        for boost in intent_boost[:1]:
            search_queries.append(f"{boost} {primary}")
    
    # 3. Single keywords with synonyms
    for keyword in keywords[:2]:
        if keyword not in [q.split()[0] for q in search_queries]:
            search_queries.append(keyword)
        
        # Add primary synonym
        synonyms = get_synonyms(keyword)
        if len(synonyms) > 1 and synonyms[1] not in search_queries:
            search_queries.append(synonyms[1])
    
    # 4. Related terms for main keyword
    if keywords:
        related = get_related_terms(keywords[0])
        for term in related[:1]:
            if term not in search_queries:
                search_queries.append(term)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_queries = []
    for q in search_queries:
        if q not in seen:
            seen.add(q)
            unique_queries.append(q)
    
    return {
        "original": query,
        "keywords": keywords,
        "stemmed": stemmed,
        "expanded": list(set(expanded)),
        "intent": intent,
        "search_queries": unique_queries[:5]  # Max 5 variations
    }


def get_optimized_search_queries(query: str) -> list[str]:
    """
    Get list of optimized search queries to try.
    
    Main entry point for the scraping engine.
    """
    result = preprocess_query(query)
    
    queries = result["search_queries"]
    
    # Ensure we have at least one query
    if not queries:
        # Fallback to cleaned original
        words = query.lower().split()
        queries = [" ".join(words[:3])]
    
    print(f"[PREPROCESS] Query: '{query}'")
    print(f"[PREPROCESS] Keywords: {result['keywords']}")
    print(f"[PREPROCESS] Intent: {result['intent']['primary_intent']} ({result['intent']['confidence']:.2f})")
    print(f"[PREPROCESS] Search variations: {queries}")
    
    return queries
