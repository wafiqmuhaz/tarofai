"""Prompt templates for Islamic knowledge answers - OPTIMIZED VERSION."""


# OPTIMIZED: More concise system prompt
SYSTEM_PROMPT = """Anda adalah asisten AI untuk menjawab pertanyaan seputar Islam dengan metodologi Salafi.

ATURAN:
1. Jawab HANYA berdasarkan konten dari sumber yang diberikan
2. DILARANG mengarang informasi
3. Sebutkan sumber referensi dengan jelas

FORMAT OUTPUT:
## Ringkasan
[Jawaban singkat 2-3 kalimat]

## Dalil
[Ayat Al-Quran atau Hadits dengan sumber/rawi]

## Penjelasan
[Penjelasan berdasarkan sumber]

## Referensi
[Daftar sumber]"""


def build_answer_prompt(query: str, sources: list[dict], max_content: int = 2000) -> str:
    """
    Build OPTIMIZED prompt for generating answer.
    
    Args:
        query: User's question
        sources: List of scraped articles
        max_content: Max chars per source (default 2000, reduced from 4000)
    """
    # Limit to 3 sources for faster processing
    limited_sources = sources[:3]
    
    sources_text = "\n\n---\n\n".join([
        f"SUMBER: {s['domain']}\nJUDUL: {s['title']}\n\nKONTEN:\n{s['content'][:max_content]}"
        for s in limited_sources
    ])
    
    return f"""PERTANYAAN: {query}

KONTEN SUMBER:

{sources_text}

---

INSTRUKSI:
1. Jawab berdasarkan konten sumber di atas
2. Format: Ringkasan → Dalil → Penjelasan → Referensi
3. Sertakan ayat/hadits jika ada
4. Sebutkan sumber setiap informasi"""


def build_no_results_response(query: str) -> str:
    """Response when no results found from approved sources."""
    return f"""## Maaf, Tidak Ditemukan

Tidak ditemukan informasi untuk: **"{query}"**

### Saran:
1. Gunakan kata kunci lebih spesifik
2. Coba istilah Bahasa Arab
3. Kunjungi langsung:
   - [KonsultasiSyariah.com](https://konsultasisyariah.com)
   - [Rumaysho.com](https://rumaysho.com)
   - [IslamQA.info](https://islamqa.info)"""


def build_intent_prompt(intent: dict, query: str, sources: list[dict]) -> str:
    """
    Build intent-specific prompt for more focused answers.
    """
    intent_instructions = {
        "definisi": "Fokus pada PENGERTIAN dan MAKNA istilah.",
        "hukum": "Fokus pada STATUS HUKUM syar'i (halal/haram/wajib/sunnah/makruh).",
        "konsekuensi": "Fokus pada AKIBAT dan HUKUMAN perbuatan.",
        "dalil": "Fokus pada DALIL Al-Quran dan Hadits.",
        "cara": "Fokus pada TATA CARA yang benar.",
        "syarat": "Fokus pada SYARAT dan RUKUN.",
    }
    
    extra_instruction = intent_instructions.get(
        intent.get("primary_intent", "general"), 
        "Berikan jawaban komprehensif."
    )
    
    base_prompt = build_answer_prompt(query, sources)
    
    return f"""{base_prompt}

FOKUS: {extra_instruction}"""
