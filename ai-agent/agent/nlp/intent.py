"""Intent detection for Islamic queries."""
import re


# Intent patterns and keywords
INTENT_PATTERNS = {
    "definisi": {
        "keywords": ["apa", "apakah", "definisi", "pengertian", "arti", "makna", "maksud"],
        "patterns": [r"apa\s+(itu|yang\s+dimaksud)", r"pengertian\s+\w+", r"definisi\s+\w+"],
        "description": "Mencari definisi atau pengertian",
    },
    "hukum": {
        "keywords": ["hukum", "boleh", "bolehkah", "halal", "haram", "wajib", "sunnah", "makruh", "mubah"],
        "patterns": [r"hukum\s+\w+", r"bolehkah\s+\w+", r"apakah\s+.*\s+(halal|haram|boleh)"],
        "description": "Mencari hukum syar'i",
    },
    "konsekuensi": {
        "keywords": ["konsekuensi", "akibat", "dampak", "hukuman", "balasan", "dosa", "siksa", "azab"],
        "patterns": [r"(konsekuensi|akibat|dampak)\s+\w+", r"dosa\s+\w+", r"hukuman\s+\w+"],
        "description": "Mencari konsekuensi atau hukuman",
    },
    "dalil": {
        "keywords": ["dalil", "ayat", "hadits", "hadis", "nash", "bukti", "quran", "sunnah"],
        "patterns": [r"dalil\s+\w+", r"ayat\s+(tentang|mengenai)", r"hadits?\s+(tentang|mengenai)"],
        "description": "Mencari dalil dari Al-Quran atau Hadits",
    },
    "cara": {
        "keywords": ["cara", "bagaimana", "langkah", "tata cara", "panduan", "tutorial"],
        "patterns": [r"cara\s+\w+", r"bagaimana\s+(cara\s+)?", r"tata\s+cara"],
        "description": "Mencari panduan atau tata cara",
    },
    "syarat": {
        "keywords": ["syarat", "rukun", "sah", "sahnya", "ketentuan", "kriteria"],
        "patterns": [r"syarat\s+\w+", r"rukun\s+\w+", r"sahnya\s+\w+"],
        "description": "Mencari syarat atau rukun",
    },
}


def detect_intent(query: str) -> dict:
    """
    Detect the intent behind a query.
    
    Args:
        query: User's query
        
    Returns:
        Dict with:
        - primary_intent: Main detected intent
        - secondary_intents: Other possible intents
        - confidence: Confidence score
        - intent_keywords: Keywords that triggered detection
    """
    query_lower = query.lower()
    intent_scores = {}
    intent_keywords = {}
    
    for intent_name, intent_data in INTENT_PATTERNS.items():
        score = 0
        matched_keywords = []
        
        # Check keywords
        for keyword in intent_data["keywords"]:
            if keyword in query_lower:
                score += 1
                matched_keywords.append(keyword)
        
        # Check patterns
        for pattern in intent_data["patterns"]:
            if re.search(pattern, query_lower):
                score += 2  # Patterns are stronger signals
                
        if score > 0:
            intent_scores[intent_name] = score
            intent_keywords[intent_name] = matched_keywords
    
    if not intent_scores:
        return {
            "primary_intent": "general",
            "secondary_intents": [],
            "confidence": 0.5,
            "intent_keywords": [],
            "description": "Pertanyaan umum"
        }
    
    # Sort by score
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    primary_intent = sorted_intents[0][0]
    primary_score = sorted_intents[0][1]
    
    # Calculate confidence
    max_possible_score = 5  # Rough estimate
    confidence = min(primary_score / max_possible_score, 1.0)
    
    secondary_intents = [intent for intent, _ in sorted_intents[1:3] if intent_scores[intent] > 0]
    
    return {
        "primary_intent": primary_intent,
        "secondary_intents": secondary_intents,
        "confidence": confidence,
        "intent_keywords": intent_keywords.get(primary_intent, []),
        "description": INTENT_PATTERNS[primary_intent]["description"]
    }


def get_intent_search_boost(intent: str) -> list[str]:
    """
    Get additional search terms based on detected intent.
    
    Args:
        intent: Detected intent name
        
    Returns:
        List of additional search terms to include
    """
    INTENT_BOOST = {
        "definisi": ["pengertian", "maksud", "arti"],
        "hukum": ["hukum", "halal haram", "fatwa"],
        "konsekuensi": ["hukuman", "dosa", "akibat", "azab"],
        "dalil": ["dalil", "ayat", "hadits", "nash"],
        "cara": ["tata cara", "panduan", "langkah"],
        "syarat": ["syarat", "rukun", "ketentuan"],
    }
    
    return INTENT_BOOST.get(intent, [])
