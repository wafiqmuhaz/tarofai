"""Prompt templates for Islamic knowledge answers."""


SYSTEM_PROMPT = """Anda adalah asisten AI khusus untuk menjawab pertanyaan seputar Islam dengan metodologi Salafi (Ahlus Sunnah wal Jamaah).

ATURAN KETAT:
1. Jawab HANYA berdasarkan konten yang diberikan dari sumber-sumber yang disetujui
2. DILARANG mengarang atau menambahkan informasi yang tidak ada di sumber
3. Jika informasi tidak lengkap, katakan dengan jujur
4. Selalu sebutkan sumber referensi dengan jelas

SUMBER YANG DISETUJUI:
- KonsultasiSyariah.com, Rumaysho.com, Almanhaj.or.id
- Muslim.or.id, Muslimah.or.id, Yufid.com
- IslamQA.info dan sumber Salafi lainnya

FORMAT OUTPUT WAJIB:
Gunakan struktur berikut dalam setiap jawaban:

## Ringkasan
[Jawaban singkat dan padat 2-3 kalimat]

## Dalil
[Sebutkan ayat Al-Quran atau Hadits yang relevan dengan sumber/rawi]

## Penjelasan
[Penjelasan lebih detail berdasarkan sumber]

## Referensi
[Daftar sumber yang digunakan]

CONTOH FORMAT:
## Ringkasan
Zina adalah dosa besar yang diharamkan dalam Islam dengan hukuman had yang berat.

## Dalil
Allah berfirman: "Dan janganlah kamu mendekati zina; sesungguhnya zina itu adalah suatu perbuatan yang keji dan suatu jalan yang buruk." (QS. Al-Isra: 32)

## Penjelasan
Berdasarkan artikel dari KonsultasiSyariah.com...

## Referensi
- KonsultasiSyariah.com: "Hukum Zina dalam Islam"
- Rumaysho.com: "Bahaya Perbuatan Zina"
"""


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
        f"SUMBER: {s['domain']}\nJUDUL: {s['title']}\nURL: {s['url']}\n\nKONTEN:\n{s['content'][:4000]}"
        for s in sources[:5]  # Limit to 5 sources
    ])
    
    return f"""PERTANYAAN PENGGUNA:
{query}

KONTEN DARI SUMBER YANG DISETUJUI:

{sources_text}

---

INSTRUKSI:
1. Jawab pertanyaan di atas HANYA berdasarkan konten sumber yang diberikan
2. Gunakan format: Ringkasan → Dalil → Penjelasan → Referensi
3. Jika ada ayat Al-Quran atau Hadits dalam sumber, sertakan dengan lengkap
4. Sebutkan dari sumber mana setiap informasi diambil
5. Jangan mengarang informasi yang tidak ada di sumber"""


def build_no_results_response(query: str) -> str:
    """Response when no results found from approved sources."""
    return f"""## Maaf, Tidak Ditemukan

Kami tidak menemukan informasi yang relevan untuk pertanyaan:
**"{query}"**

### Saran:
1. Gunakan kata kunci yang lebih spesifik
2. Coba istilah dalam Bahasa Arab atau sinonimnya
3. Kunjungi langsung sumber-sumber berikut:
   - [KonsultasiSyariah.com](https://konsultasisyariah.com)
   - [Rumaysho.com](https://rumaysho.com)
   - [Muslim.or.id](https://muslim.or.id)
   - [IslamQA.info](https://islamqa.info)

### Catatan:
Sistem ini hanya mengambil data dari sumber-sumber Salafi yang terpercaya untuk menjaga akurasi informasi."""


def build_intent_prompt(intent: dict, query: str, sources: list[dict]) -> str:
    """
    Build intent-specific prompt for more focused answers.
    
    Args:
        intent: Detected intent from preprocessor
        query: User's question
        sources: List of scraped articles
    """
    intent_instructions = {
        "definisi": "Fokuskan jawaban pada PENGERTIAN dan MAKNA dari istilah yang ditanyakan.",
        "hukum": "Fokuskan jawaban pada STATUS HUKUM syar'i (halal/haram/wajib/sunnah/makruh).",
        "konsekuensi": "Fokuskan jawaban pada AKIBAT, HUKUMAN, atau KONSEKUENSI dari perbuatan tersebut.",
        "dalil": "Fokuskan jawaban pada DALIL dari Al-Quran dan Hadits dengan lengkap.",
        "cara": "Fokuskan jawaban pada TATA CARA atau LANGKAH-LANGKAH yang benar.",
        "syarat": "Fokuskan jawaban pada SYARAT-SYARAT dan RUKUN yang harus dipenuhi.",
    }
    
    extra_instruction = intent_instructions.get(
        intent.get("primary_intent", "general"), 
        "Berikan jawaban yang komprehensif."
    )
    
    base_prompt = build_answer_prompt(query, sources)
    
    return f"""{base_prompt}

FOKUS KHUSUS:
{extra_instruction}

Intent terdeteksi: {intent.get('primary_intent', 'general')} (confidence: {intent.get('confidence', 0):.2f})"""
