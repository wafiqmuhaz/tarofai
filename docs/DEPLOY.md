# 🚀 Panduan Deployment Tarofa

Dokumentasi lengkap untuk men-deploy Tarofa ke production environment.

---

## 📋 Daftar Isi

- [Overview](#overview)
- [Persiapan](#persiapan)
- [Opsi Deployment](#opsi-deployment)
- [Deploy ke Netlify (Frontend)](#deploy-ke-netlify-frontend)
- [Deploy ke Railway (Backend + Agent)](#deploy-ke-railway-backend--agent)
- [Deploy ke Render](#deploy-ke-render)
- [Environment Variables](#environment-variables)
- [Troubleshooting](#troubleshooting)

---

## 📖 Overview

Tarofa terdiri dari 3 komponen yang perlu di-deploy:

| Komponen | Teknologi | Rekomendasi Platform |
|----------|-----------|---------------------|
| Frontend | React + Vite | **Netlify** (gratis) |
| Backend API | FastAPI | Railway / Render |
| AI Agent | FastAPI | Railway / Render |

### Arsitektur Deployment

```
┌─────────────────────────────────┐
│   Frontend (Netlify)            │
│   https://tarofa.netlify.app    │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   Backend API (Railway/Render)  │
│   https://tarofa-api.up.railway.app │
└─────────────┬───────────────────┘
              │
              ▼
┌─────────────────────────────────┐
│   AI Agent (Railway/Render)     │
│   https://tarofa-agent.up.railway.app │
└─────────────────────────────────┘
```

---

## 🛠️ Persiapan

### 1. Dapatkan OpenRouter API Key

1. Kunjungi [openrouter.ai](https://openrouter.ai)
2. Sign up / Login
3. Buat API Key baru
4. Simpan API Key dengan aman

### 2. Persiapkan Repository

```bash
# Pastikan semua perubahan sudah di-commit
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 3. Build Frontend untuk Production

```bash
cd frontend
npm install
npm run build
# Output akan ada di folder `dist/`
```

---

## 🌐 Deploy ke Netlify (Frontend)

Netlify adalah platform gratis untuk hosting static sites dan frontend apps.

### Langkah 1: Buat Akun Netlify

1. Kunjungi [netlify.com](https://netlify.com)
2. Sign up dengan GitHub/GitLab/Email

### Langkah 2: Deploy via Git

**Opsi A: Connect Git Repository**

1. Klik **"Add new site"** → **"Import an existing project"**
2. Pilih **GitHub** dan authorize
3. Pilih repository **tarofa**
4. Konfigurasi build:
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/dist
   ```
5. Klik **"Deploy site"**

**Opsi B: Manual Deploy (Drag & Drop)**

1. Build frontend locally:
   ```bash
   cd frontend
   npm run build
   ```
2. Buka [app.netlify.com](https://app.netlify.com)
3. Drag folder `frontend/dist` ke area deploy

### Langkah 3: Konfigurasi Environment Variables

1. Buka **Site settings** → **Environment variables**
2. Tambahkan:
   ```
   VITE_API_URL = https://your-backend-url.railway.app
   ```

### Langkah 4: Konfigurasi Redirects (SPA)

Buat file `frontend/public/_redirects`:
```
/*    /index.html   200
```

Atau buat file `frontend/netlify.toml`:
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

### Langkah 5: Custom Domain (Opsional)

1. Buka **Domain settings**
2. Klik **"Add custom domain"**
3. Ikuti instruksi untuk setup DNS

**Hasil**: `https://your-site-name.netlify.app`

---

## 🚂 Deploy ke Railway (Backend + Agent)

Railway menyediakan free tier untuk hosting backend services.

### Langkah 1: Buat Akun Railway

1. Kunjungi [railway.app](https://railway.app)
2. Sign up dengan GitHub

### Langkah 2: Deploy Backend API

1. Klik **"New Project"** → **"Deploy from GitHub repo"**
2. Pilih repository tarofa
3. Railway akan auto-detect bahasa

4. Konfigurasi service:
   - **Root Directory**: `backend`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

5. Set Environment Variables:
   ```
   AGENT_URL = https://your-agent-service.railway.app
   ```

### Langkah 3: Deploy AI Agent

1. Dalam project yang sama, klik **"New"** → **"GitHub Repo"**
2. Pilih repo yang sama, tapi set:
   - **Root Directory**: `ai-agent`
   - **Start Command**: `uvicorn agent.main:app --host 0.0.0.0 --port $PORT`

3. Set Environment Variables:
   ```
   OPENROUTER_API_KEY = sk-or-v1-xxxxx
   OPENROUTER_BASE_URL = https://openrouter.ai/api/v1
   OPENROUTER_MODEL = google/gemini-2.0-flash-exp:free
   ```

### Langkah 4: Generate Domain

1. Buka service settings
2. Klik **"Generate Domain"**
3. Catat URL yang dihasilkan

### Railway Procfile (Opsional)

Buat file `backend/Procfile`:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Buat file `ai-agent/Procfile`:
```
web: uvicorn agent.main:app --host 0.0.0.0 --port $PORT
```

---

## 🎨 Deploy ke Render

Render adalah alternatif lain dengan free tier.

### Langkah 1: Buat Akun Render

1. Kunjungi [render.com](https://render.com)
2. Sign up dengan GitHub

### Langkah 2: Deploy Backend

1. Klik **"New"** → **"Web Service"**
2. Connect GitHub repository
3. Konfigurasi:
   ```
   Name: tarofa-backend
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. Set Environment Variables
5. Klik **"Create Web Service"**

### Langkah 3: Deploy AI Agent

Ulangi langkah yang sama dengan:
```
Name: tarofa-agent
Root Directory: ai-agent
Build Command: pip install -r requirements.txt
Start Command: uvicorn agent.main:app --host 0.0.0.0 --port $PORT
```

### Render YAML Config (Opsional)

Buat file `render.yaml` di root:
```yaml
services:
  - type: web
    name: tarofa-backend
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: AGENT_URL
        sync: false
    
  - type: web
    name: tarofa-agent  
    runtime: python
    rootDir: ai-agent
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn agent.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
```

---

## 🔐 Environment Variables

### Backend (.env)
```env
# AI Agent URL (Railway/Render URL)
AGENT_URL=https://tarofa-agent.up.railway.app
```

### AI Agent (.env)
```env
# OpenRouter Configuration (WAJIB)
OPENROUTER_API_KEY=sk-or-v1-xxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
```

### Frontend (.env.production)
```env
VITE_API_URL=https://tarofa-backend.up.railway.app
```

---

## 🔧 Best Practices

### 1. Security
- ✅ Jangan commit API keys ke Git
- ✅ Gunakan environment variables
- ✅ Enable HTTPS (otomatis di Netlify/Railway/Render)

### 2. Performance
- ✅ Enable caching di CDN
- ✅ Minify assets (otomatis saat build)
- ✅ Gunakan gzip compression

### 3. Monitoring
- ✅ Cek logs di dashboard platform
- ✅ Setup alerts untuk errors
- ✅ Monitor response times

### 4. CORS Configuration

Update `backend/app/main.py` untuk production:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tarofa.netlify.app",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐛 Troubleshooting

### Frontend tidak bisa connect ke Backend

1. Cek `VITE_API_URL` sudah benar
2. Cek CORS sudah dikonfigurasi
3. Cek backend sudah running

### Backend error "AGENT_URL not found"

1. Pastikan environment variable `AGENT_URL` sudah di-set
2. Cek AI Agent service sudah running

### AI Agent error "OPENROUTER_API_KEY not set"

1. Pastikan API key sudah di-set di environment
2. Cek API key masih valid di OpenRouter dashboard

### Slow Response Time

1. Cek region deployment (pilih yang dekat dengan target users)
2. Upgrade ke paid tier jika perlu
3. Cek logs untuk bottleneck

### Build Failed

1. Cek logs untuk error message
2. Pastikan `requirements.txt` / `package.json` lengkap
3. Test build locally sebelum push

---

## 📊 Checklist Deployment

### Pre-Deployment
- [ ] Semua perubahan sudah di-commit
- [ ] API keys sudah siap
- [ ] Build local berhasil

### Frontend (Netlify)
- [ ] Repository connected
- [ ] Build settings configured
- [ ] Environment variables set
- [ ] Redirects configured
- [ ] Site live

### Backend (Railway/Render)
- [ ] Service deployed
- [ ] Environment variables set
- [ ] CORS configured
- [ ] Health check passing

### AI Agent (Railway/Render)
- [ ] Service deployed
- [ ] OpenRouter API key set
- [ ] Health check passing

### Post-Deployment
- [ ] Test full flow (search query)
- [ ] Verify caching works
- [ ] Check response times
- [ ] Monitor for errors

---

## 📞 Support

Jika mengalami masalah saat deployment:

1. Cek dokumentasi platform masing-masing
2. Lihat logs untuk error messages
3. Buka issue di repository
