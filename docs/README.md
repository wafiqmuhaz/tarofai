# 🕌 Tarofa - Islamic AI Search Engine

> AI-powered search engine untuk menjawab pertanyaan seputar Islam berdasarkan sumber-sumber Salafi yang terpercaya.

## 📋 Daftar Isi

- [Tentang Project](#tentang-project)
- [Fitur Utama](#fitur-utama)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Struktur Folder](#struktur-folder)
- [Teknologi](#teknologi)
- [Alur Kerja Sistem](#alur-kerja-sistem)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Konfigurasi](#konfigurasi)

---

## 📖 Tentang Project

**Tarofa** adalah AI-powered search engine yang dirancang khusus untuk menjawab pertanyaan seputar Islam dengan metodologi Salafi (Ahlus Sunnah wal Jamaah).

### Tujuan
- Menyediakan jawaban Islam yang akurat dan berbasis dalil
- Memastikan semua referensi berasal dari sumber yang terpercaya
- Memberikan pengalaman pencarian yang mirip dengan ChatGPT/Gemini

### Ruang Lingkup
Sistem ini **HANYA** mengambil referensi dari sumber-sumber yang diizinkan (whitelist):

| Sumber | Domain | Bahasa |
|--------|--------|--------|
| Konsultasi Syariah | konsultasisyariah.com | Indonesia |
| Rumaysho | rumaysho.com | Indonesia |
| Almanhaj | almanhaj.or.id | Indonesia |
| Muslim.or.id | muslim.or.id | Indonesia |
| Muslimah.or.id | muslimah.or.id | Indonesia |
| Yufid | yufid.com | Indonesia |
| IslamQA | islamqa.info | Multi |

---

## ✨ Fitur Utama

- 🔍 **Smart Search** - Pencarian dengan NLP preprocessing dan intent detection
- ⚡ **Parallel Scraping** - Scraping 7 sumber secara bersamaan untuk respons cepat
- 🧠 **AI Summarization** - Ringkasan jawaban menggunakan LLM (Gemini via OpenRouter)
- 💾 **Smart Caching** - Fuzzy matching untuk cache hit yang lebih tinggi
- 📚 **Source Citations** - Setiap jawaban disertai sumber referensi yang jelas
- 🎯 **Intent-Aware** - Respons disesuaikan dengan jenis pertanyaan (hukum, dalil, cara, dll)

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│                    (React + Vite - Port 5173)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         BACKEND API                                  │
│                    (FastAPI - Port 8000)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │   Routes    │  │   Config    │  │  Services   │                 │
│  │  /search    │  │   .env      │  │ AgentClient │                 │
│  └─────────────┘  └─────────────┘  └─────────────┘                 │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         AI AGENT                                     │
│                    (FastAPI - Port 3001)                            │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │    NLP    │  │  Scraper  │  │    LLM    │  │   Cache   │       │
│  │Preprocessor│  │  Engine   │  │  Client   │  │  Manager  │       │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
            ┌───────────┐   ┌───────────┐   ┌───────────┐
            │ Approved  │   │ OpenRouter│   │   JSON    │
            │ Websites  │   │    API    │   │   Cache   │
            │(Whitelist)│   │  (Gemini) │   │   Files   │
            └───────────┘   └───────────┘   └───────────┘
```

### Data Flow Diagram

```
User Query
    │
    ▼
┌─────────────────┐
│ 1. Preprocess   │ ──→ Extract keywords, detect intent
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Cache Check  │ ──→ Exact match OR fuzzy match (75% similarity)
└────────┬────────┘
         │
    ┌────┴────┐
    │  HIT?   │
    └────┬────┘
    YES  │  NO
    ▼    │
┌────────┐   │
│ Return │   ▼
│ Cached │  ┌─────────────────┐
└────────┘  │ 3. Parallel     │
            │    Scraping     │ ──→ 7 sources simultaneously
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ 4. LLM Generate │ ──→ Summarize with citations
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ 5. Cache Result │
            └────────┬────────┘
                     │
                     ▼
               Return Answer
```

---

## 📁 Struktur Folder

```
tarofai/
├── 📁 ai-agent/                 # AI Agent Service
│   ├── 📁 agent/
│   │   ├── 📁 cache/            # Cache management
│   │   │   └── manager.py       # Fuzzy cache matching
│   │   ├── 📁 llm/              # LLM integration
│   │   │   ├── client.py        # OpenRouter API client
│   │   │   └── prompts.py       # Prompt templates
│   │   ├── 📁 nlp/              # NLP processing
│   │   │   ├── preprocessor.py  # Query preprocessing
│   │   │   ├── intent.py        # Intent detection
│   │   │   └── synonyms.py      # Synonym expansion
│   │   ├── 📁 scraper/          # Web scraping
│   │   │   ├── engine.py        # Parallel scraping engine
│   │   │   ├── whitelist.py     # Approved domains
│   │   │   └── normalizer.py    # Content extraction
│   │   ├── main.py              # FastAPI application
│   │   └── performance.py       # Performance tracking
│   └── requirements.txt
│
├── 📁 backend/                  # Backend API
│   ├── 📁 app/
│   │   ├── 📁 routes/
│   │   │   └── search.py        # Search endpoint
│   │   ├── 📁 services/
│   │   │   └── agent_client.py  # AI Agent HTTP client
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI application
│   └── requirements.txt
│
├── 📁 frontend/                 # Frontend UI
│   ├── 📁 src/
│   │   ├── 📁 components/       # React components
│   │   ├── 📁 pages/            # Page components
│   │   └── App.jsx              # Main app
│   ├── package.json
│   └── vite.config.js
│
├── 📁 serverData/               # Runtime data
│   ├── 📁 cache/                # Answer cache (JSON)
│   └── 📁 scraped/              # Scraped data cache
│
├── 📁 docs/                     # Documentation
│   ├── README.md                # This file
│   └── DEPLOY.md                # Deployment guide
│
├── .env.example                 # Environment template
├── .gitignore
└── run.sh                       # Development runner script
```

---

## 🛠️ Teknologi

### Backend & AI Agent
| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| Python | 3.11+ | Runtime |
| FastAPI | 0.115.0 | REST API framework |
| aiohttp | 3.10.0 | Async HTTP for scraping |
| httpx | 0.27.0 | HTTP client for LLM |
| BeautifulSoup4 | 4.12.3 | HTML parsing |
| lxml | 5.3.0 | Fast XML/HTML parser |
| Pydantic | 2.10+ | Data validation |

### Frontend
| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| React | 18.x | UI Library |
| Vite | 5.x | Build tool |
| JavaScript | ES6+ | Language |

### AI/LLM
| Service | Model | Fungsi |
|---------|-------|--------|
| OpenRouter | google/gemini-2.0-flash-exp:free | LLM API |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm atau yarn

### 1. Clone Repository
```bash
git clone https://github.com/your-repo/tarofa.git
cd tarofa
```

### 2. Setup Environment
```bash
cp .env.example .env
# Edit .env dan isi OPENROUTER_API_KEY
```

### 3. Jalankan
```bash
./run.sh up
```

Akses:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **AI Agent**: http://localhost:3001
- **API Docs**: http://localhost:8000/docs

### Commands
```bash
./run.sh up        # Start dengan realtime logs
./run.sh bg        # Start di background
./run.sh down      # Stop semua services
./run.sh status    # Cek health services
./run.sh logs      # Lihat logs
```

---

## 📡 API Reference

### POST /search

Mencari jawaban untuk pertanyaan Islam.

**Request:**
```json
{
  "query": "Apa hukum musik dalam Islam?"
}
```

**Response:**
```json
{
  "query": "Apa hukum musik dalam Islam?",
  "answer": "## Ringkasan\n...",
  "sources": [
    {
      "title": "Hukum Musik dalam Islam",
      "url": "https://konsultasisyariah.com/...",
      "domain": "konsultasisyariah.com"
    }
  ],
  "cached": false,
  "intent": "hukum",
  "processing_time": 12.5
}
```

---

## ⚙️ Konfigurasi

### Environment Variables

| Variable | Wajib | Deskripsi |
|----------|-------|-----------|
| `OPENROUTER_API_KEY` | ✅ | API key dari OpenRouter |
| `OPENROUTER_BASE_URL` | ❌ | Base URL (default: openrouter.ai) |
| `OPENROUTER_MODEL` | ❌ | Model ID (default: gemini-2.0-flash-exp) |
| `BACKEND_PORT` | ❌ | Port backend (default: 8000) |
| `AGENT_PORT` | ❌ | Port AI agent (default: 3001) |
| `VITE_API_URL` | ❌ | URL backend untuk frontend |

---

## 📄 Lisensi

MIT License - Lihat file LICENSE untuk detail.

---

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buat Pull Request
