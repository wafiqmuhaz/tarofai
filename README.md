# Tarofa

An AI-powered Islamic search engine providing Salafi-methodology answers from strictly curated sources.

## Features

- 🔍 **Intelligent Search** - Ask questions and get AI-generated answers
- 📚 **Curated Sources** - Data from trusted Salafi websites only
- ⚡ **Fast Responses** - Cached results for repeated queries
- 🔗 **Source Citations** - Every answer includes source references

## Approved Data Sources

- konsultasisyariah.com
- rumaysho.com  
- almanhaj.or.id
- salafycirebon.com

## Quick Start

```bash
# Start all services
./run.sh up

# Stop all services
./run.sh down

# View logs
./run.sh logs
```

## Project Structure

```
tarofai/
├── backend/        # FastAPI backend
├── ai-agent/       # Scraping + LLM agent
├── frontend/       # React/Vite UI
├── serverData/     # Persistent storage
├── sandbox/        # Testing environment
├── mockserver/     # API simulation
└── run.sh          # Orchestration
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

## Technology Stack

- **Backend**: Python 3.11+, FastAPI
- **AI Agent**: Python, aiohttp, BeautifulSoup4
- **Frontend**: React 18, Vite
- **LLM**: OpenRouter (gemini-2.0-flash-exp)
