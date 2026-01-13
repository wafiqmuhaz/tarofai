"""Prompt templates for Islamic knowledge answers."""


SYSTEM_PROMPT = """Anda adalah asisten AI khusus untuk menjawab pertanyaan seputar Islam dengan metodologi Salafi (Ahlus Sunnah wal Jamaah).

ATURAN PENTING:
1. Jawab HANYA berdasarkan konten yang diberikan dari sumber-sumber yang disetujui
2. Jangan menambahkan pendapat pribadi atau spekulasi
3. Selalu sebutkan sumber referensi
4. Gunakan bahasa Indonesia yang baik dan mudah dipahami
5. Jika informasi tidak tersedia dalam sumber, katakan dengan jujur

SUMBER YANG DISETUJUI:
- KonsultasiSyariah.com
- Rumaysho.com  
- Almanhaj.or.id
- SalafyCirebon.com

FORMAT JAWABAN:
- Mulai dengan ringkasan singkat
- Jelaskan dalil dari Al-Quran dan Hadits jika ada
- Berikan penjelasan yang mudah dipahami
- Akhiri dengan referensi sumber"""


def build_answer_prompt(query: str, sources: list[dict]) -> str:
    """
    Build prompt for generating answer from scraped sources.
    
    Args:
        query: User's question
        sources: List of scraped articles
        
    Returns:
        Formatted prompt string
    """
    sources_text = "\n\n---\n\n".join([
        f"SUMBER: {s['domain']}\nJUDUL: {s['title']}\nURL: {s['url']}\n\nKONTEN:\n{s['content'][:3000]}"
        for s in sources
    ])
    
    return f"""Pertanyaan pengguna: {query}

KONTEN DARI SUMBER-SUMBER YANG DISETUJUI:

{sources_text}

---

Berdasarkan konten di atas, berikan jawaban yang komprehensif untuk pertanyaan pengguna. 
Pastikan untuk menyebutkan sumber referensi dari mana informasi diambil."""


def build_no_results_response(query: str) -> str:
    """Response when no results found from approved sources."""
    return f"""Mohon maaf, kami tidak menemukan informasi yang relevan untuk pertanyaan "{query}" dari sumber-sumber yang disetujui.

Silakan coba:
1. Gunakan kata kunci yang berbeda
2. Pertanyaan yang lebih spesifik
3. Kunjungi langsung situs-situs berikut:
   - konsultasisyariah.com
   - rumaysho.com
   - almanhaj.or.id
   - salafycirebon.com"""
