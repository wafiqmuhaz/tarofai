"""Islamic terminology synonyms and semantic expansion."""

# Synonym mappings for Islamic terms (Indonesian)
SYNONYMS_ID = {
    # Zina related
    "zina": ["berzina", "perzinaan", "berbuat zina", "perbuatan zina"],
    "berzina": ["zina", "perzinaan", "berbuat zina"],
    "konsekuensi": ["hukuman", "akibat", "dampak", "balasan", "siksa"],
    "hukuman": ["konsekuensi", "akibat", "had", "sanksi", "balasan"],
    
    # Prayer related
    "sholat": ["salat", "shalat", "sembahyang"],
    "shalat": ["sholat", "salat", "sembahyang"],
    "salat": ["sholat", "shalat", "sembahyang"],
    "jumat": ["jum'at", "jumaat"],
    
    # Fasting related
    "puasa": ["shaum", "shiyam", "berpuasa"],
    "shaum": ["puasa", "shiyam"],
    "ramadhan": ["ramadan", "bulan puasa"],
    
    # Pilgrimage
    "haji": ["hajj", "berhaji", "ibadah haji"],
    "umrah": ["umroh", "ibadah umrah"],
    
    # General Islamic terms
    "hukum": ["dalil", "fatwa", "ketetapan", "ketentuan"],
    "dalil": ["bukti", "nash", "ayat", "hadits", "hadis"],
    "hadits": ["hadis", "sunnah", "atsar"],
    "hadis": ["hadits", "sunnah", "atsar"],
    "bid'ah": ["bidah", "perkara baru"],
    "syirik": ["kesyirikan", "menyekutukan"],
    "tauhid": ["tawhid", "keesaan"],
    "aqidah": ["akidah", "keyakinan", "kepercayaan"],
    "fiqih": ["fikih", "fiqh", "hukum islam"],
    "fikih": ["fiqih", "fiqh", "hukum islam"],
    
    # Actions
    "wajib": ["fardhu", "fardu", "harus"],
    "sunnah": ["sunah", "mustahab", "dianjurkan"],
    "haram": ["dilarang", "diharamkan", "terlarang"],
    "halal": ["dibolehkan", "dihalalkan", "mubah"],
    "makruh": ["dibenci", "tidak disukai"],
    
    # People
    "ulama": ["ustadz", "ustaz", "syaikh", "kyai"],
    "nabi": ["rasul", "rasulullah"],
    "sahabat": ["shahabat", "para sahabat"],
}

# English synonyms
SYNONYMS_EN = {
    "zina": ["fornication", "adultery", "sexual sin"],
    "prayer": ["salah", "salat", "sholat"],
    "fasting": ["sawm", "puasa"],
    "hajj": ["pilgrimage", "haji"],
    "haram": ["forbidden", "prohibited", "unlawful"],
    "halal": ["permissible", "lawful", "allowed"],
    "sunnah": ["prophetic tradition", "recommended"],
    "bidah": ["innovation", "bid'ah"],
}


def get_synonyms(word: str) -> list[str]:
    """
    Get synonyms for a word.
    
    Args:
        word: Input word
        
    Returns:
        List of synonyms including the original word
    """
    word_lower = word.lower()
    
    # Check Indonesian synonyms
    if word_lower in SYNONYMS_ID:
        return [word_lower] + SYNONYMS_ID[word_lower]
    
    # Check if word is a synonym of something else
    for key, synonyms in SYNONYMS_ID.items():
        if word_lower in synonyms:
            return [word_lower, key] + [s for s in synonyms if s != word_lower]
    
    # Check English
    if word_lower in SYNONYMS_EN:
        return [word_lower] + SYNONYMS_EN[word_lower]
    
    return [word_lower]


def expand_query_synonyms(keywords: list[str]) -> list[str]:
    """
    Expand keywords with synonyms.
    
    Args:
        keywords: List of keywords
        
    Returns:
        Expanded list with synonyms
    """
    expanded = set()
    
    for keyword in keywords:
        synonyms = get_synonyms(keyword)
        expanded.update(synonyms[:3])  # Limit to top 3 synonyms per word
    
    return list(expanded)


def get_related_terms(keyword: str) -> list[str]:
    """
    Get conceptually related terms for semantic expansion.
    """
    # Concept relationships
    RELATED = {
        "zina": ["hukuman zina", "dosa zina", "had zina", "taubat zina"],
        "berzina": ["hukuman zina", "dosa zina", "had zina", "taubat zina"],
        "sholat": ["wudhu", "rukun sholat", "sunnah sholat", "waktu sholat"],
        "puasa": ["sahur", "berbuka", "ramadhan", "sunnah puasa"],
        "haji": ["manasik", "ihram", "tawaf", "sa'i", "wukuf"],
    }
    
    keyword_lower = keyword.lower()
    return RELATED.get(keyword_lower, [])
