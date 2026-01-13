"""Mock server for testing without real scraping/LLM calls."""
from flask import Flask, jsonify, request

app = Flask(__name__)


MOCK_RESPONSES = {
    "default": {
        "answer": """Alhamdulillah, berdasarkan sumber-sumber yang disetujui:

**Tentang Pertanyaan Anda:**

Ini adalah jawaban mock untuk keperluan testing. Dalam implementasi nyata, jawaban ini akan dihasilkan oleh AI berdasarkan konten yang di-scrape dari sumber-sumber Salafi terpercaya.

**Dalil:**
- "Barangsiapa yang mengerjakan suatu amalan yang tidak ada contohnya dari kami, maka amalan itu tertolak." (HR. Muslim)

**Kesimpulan:**
Selalu merujuk kepada Al-Quran dan Sunnah dengan pemahaman Salafus Shalih.

Wallahu a'lam.""",
        "sources": [
            {
                "title": "Artikel Mock - konsultasisyariah.com",
                "url": "https://konsultasisyariah.com/mock-article",
                "domain": "konsultasisyariah.com"
            },
            {
                "title": "Artikel Mock - rumaysho.com", 
                "url": "https://rumaysho.com/mock-article",
                "domain": "rumaysho.com"
            }
        ],
        "cached": False
    }
}


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "tarofa-mockserver"})


@app.route('/process', methods=['POST'])
def process():
    """Mock process endpoint - returns fake response."""
    data = request.get_json()
    query = data.get('query', '')
    
    # Return mock response
    response = MOCK_RESPONSES["default"].copy()
    response["query"] = query
    
    return jsonify(response)


@app.route('/api/search', methods=['POST'])
def search():
    """Mock search endpoint for full mock mode."""
    data = request.get_json()
    query = data.get('query', '')
    
    response = MOCK_RESPONSES["default"].copy()
    response["query"] = query
    
    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)
