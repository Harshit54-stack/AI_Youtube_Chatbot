# 🚀 Deployment Guide — YouTube RAG Chatbot

Step-by-step deployment instructions for Render, Railway, and Docker.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Render (Recommended)](#2-render-recommended)
3. [Railway](#3-railway)
4. [Docker (Self-hosted)](#4-docker-self-hosted)
5. [Environment Variables Reference](#5-environment-variables-reference)
6. [Post-Deployment Checklist](#6-post-deployment-checklist)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Prerequisites

Before deploying, ensure you have:

- [ ] A **Groq API key** — free at [console.groq.com](https://console.groq.com)
- [ ] The project pushed to a **GitHub repository**
- [ ] Python 3.11+ (for local testing only)

---

## 2. Render (Recommended)

Render is the easiest deployment path — the `render.yaml` blueprint is already
configured in the repo root.

### 2a. Deploy via Blueprint (automatic)

1. Push your repo to GitHub.
2. Go to [render.com](https://render.com) → **New** → **Blueprint**.
3. Connect your GitHub account and select the `AI_Youtube_Chatbot` repo.
4. Render will auto-detect `render.yaml` and pre-fill all settings.
5. Click **Apply**.

### 2b. Set the API key (required)

After the service is created:

1. Go to your service in the Render dashboard.
2. Click **Environment** tab.
3. Add a **new secret environment variable**:
   - Key: `GROQ_API_KEY`
   - Value: `gsk_xxxxxxxxxxxx...` (your key from console.groq.com)
4. Click **Save Changes** → the service will automatically redeploy.

### 2c. Verify deployment

```bash
# Replace with your Render URL
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "api": "YouTube RAG Chatbot",
  "version": "3.0.0",
  "environment": "production",
  "llm_provider": "Groq Cloud",
  "llm_model": "llama-3.1-8b-instant"
}
```

### 2d. Update CORS for your frontend

Once you deploy your React frontend (e.g., on Vercel), add its URL to `render.yaml`:

```yaml
- key: CORS_ORIGINS
  value: '["https://your-react-app.vercel.app","http://localhost:5173"]'
```

Or set it directly in the Render dashboard.

### Render Notes

| Setting | Value |
|---|---|
| **Plan** | Free (512 MB RAM) — works for demos |
| **Upgrade to** | Starter ($7/mo) for production |
| **Region** | Oregon (US West) — choose closest to users |
| **Cold start** | ~30s on free tier after inactivity |
| **Auto-deploy** | Enabled — every `git push` to main triggers redeploy |

---

## 3. Railway

Railway provides a more developer-friendly CLI experience and generous free credits.

### 3a. Install Railway CLI

```bash
# macOS / Linux
curl -fsSL https://railway.app/install.sh | sh

# Windows (PowerShell)
iwr https://railway.app/install.ps1 -useb | iex

# Or via npm
npm install -g @railway/cli
```

### 3b. Login and initialise

```bash
railway login
railway init
```

When prompted:
- **Project name**: `yt-rag-chatbot`
- **Template**: Empty project

### 3c. Deploy

```bash
railway up
```

### 3d. Set environment variables

```bash
# Required
railway variables set GROQ_API_KEY=gsk_xxxxxxxxxxxx...

# Optional — configure model
railway variables set LLM_MODEL_NAME=llama-3.1-8b-instant
railway variables set LLM_TEMPERATURE=0.0
railway variables set LLM_MAX_TOKENS=1024
railway variables set LLM_TIMEOUT=60
railway variables set LOG_LEVEL=INFO
railway variables set APP_ENV=production
```

### 3e. Configure start command

In the Railway dashboard → your service → **Settings** → **Start Command**:

```
uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 1
```

### 3f. Verify

```bash
# Get your Railway URL
railway open

# Health check
curl https://your-service.railway.app/health
```

### Railway Notes

| Feature | Detail |
|---|---|
| **Free credits** | $5/month on Hobby plan |
| **Deploy trigger** | Every `git push` or `railway up` |
| **Environment** | Set per-service in dashboard or via CLI |
| **Logs** | `railway logs --tail` |

---

## 4. Docker (Self-hosted)

Use Docker to run the backend on any server (VPS, EC2, DigitalOcean, etc.).

### 4a. Build the image

```bash
# From the project root
docker build -t yt-rag-chatbot:latest .
```

The multi-stage Dockerfile produces a lean ~350 MB image using Python 3.11-slim.

### 4b. Run with environment variables

```bash
docker run -d \
  --name yt-rag-chatbot \
  -p 8000:8000 \
  -e GROQ_API_KEY=gsk_xxxxxxxxxxxx... \
  -e LLM_MODEL_NAME=llama-3.1-8b-instant \
  -e APP_ENV=production \
  -e LOG_LEVEL=INFO \
  --restart unless-stopped \
  yt-rag-chatbot:latest
```

### 4c. Run with a .env file

```bash
docker run -d \
  --name yt-rag-chatbot \
  -p 8000:8000 \
  --env-file backend/.env \
  --restart unless-stopped \
  yt-rag-chatbot:latest
```

### 4d. Docker Compose (recommended for production)

Create `docker-compose.yml` in the project root:

```yaml
version: "3.9"

services:
  yt-rag-chatbot:
    build: .
    image: yt-rag-chatbot:latest
    container_name: yt-rag-chatbot
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    environment:
      - APP_ENV=production
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "python", "-c",
             "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"]
      interval: 30s
      timeout: 10s
      start_period: 60s
      retries: 3
```

```bash
# Start
docker compose up -d

# Logs
docker compose logs -f

# Stop
docker compose down
```

### 4e. Push to Docker Hub (optional)

```bash
docker tag yt-rag-chatbot:latest yourusername/yt-rag-chatbot:latest
docker push yourusername/yt-rag-chatbot:latest
```

---

## 5. Environment Variables Reference

Set these in your deployment platform's dashboard or in `backend/.env`:

```env
# ── REQUIRED ───────────────────────────────────────────────────────────────────
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ── LLM Configuration ──────────────────────────────────────────────────────────
LLM_MODEL_NAME=llama-3.1-8b-instant    # fastest; use llama-3.3-70b-versatile for quality
LLM_TEMPERATURE=0.0                     # 0 = deterministic (best for RAG)
LLM_MAX_TOKENS=1024                     # max tokens in response
LLM_TIMEOUT=60                          # seconds before timeout
LLM_MAX_RETRIES=2                       # auto-retries on transient errors

# ── Embeddings (local, no API key needed) ──────────────────────────────────────
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# ── RAG Pipeline ───────────────────────────────────────────────────────────────
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVER_K=4
VECTOR_STORE_CACHE_SIZE=10    # reduce to 5-10 on free-tier (512 MB RAM)

# ── Server ─────────────────────────────────────────────────────────────────────
CORS_ORIGINS=["https://your-frontend.vercel.app","http://localhost:5173"]
LOG_LEVEL=INFO
APP_ENV=production
PYTHONUNBUFFERED=1
```

---

## 6. Post-Deployment Checklist

After deploying, verify each item:

- [ ] `GET /health` returns `"status": "ok"`
- [ ] `GET /models` returns the model catalogue
- [ ] `POST /ask` with a test video returns a grounded answer
- [ ] Swagger UI loads at `/docs`
- [ ] Logs show requests with request IDs and latency
- [ ] `GROQ_API_KEY` is set in the platform dashboard (not in code)
- [ ] CORS origins include your frontend URL
- [ ] `APP_ENV` is set to `production`

### Test POST /ask via curl

```bash
curl -X POST https://your-service.onrender.com/ask \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=Gfr50f6ZBvo",
    "question": "What is the main topic of this video?"
  }'
```

---

## 7. Troubleshooting

### ❌ 503 — Cannot reach Groq API

- Check `GROQ_API_KEY` is set correctly in the platform dashboard.
- Verify the key starts with `gsk_` and is from [console.groq.com](https://console.groq.com).
- Check platform outbound internet access (some free tiers block external APIs).

### ❌ 422 — GROQ_API_KEY validation failed at startup

- The key is set but looks wrong (doesn't start with `gsk_`).
- Regenerate the key at console.groq.com → API Keys.

### ❌ 500 — LLM_GENERATION_ERROR: rate limit

- On the free Groq tier: 30 requests/minute for most models.
- Switch to `llama-3.1-8b-instant` which has higher free-tier limits.
- Or wait 60 seconds between requests.

### ❌ Render cold start timeout

- Free tier sleeps after 15 minutes of inactivity.
- Cold start takes ~30-60s (embedding model loading).
- Upgrade to **Starter** plan to disable sleep.
- Or use a cron job / uptime monitor to ping `/health` every 10 minutes.

### ❌ Out of memory on free tier

- Free Render/Railway instances have 512 MB RAM.
- The embedding model (`all-MiniLM-L6-v2`) uses ~90 MB.
- Each FAISS index uses ~10-50 MB depending on video length.
- Reduce `VECTOR_STORE_CACHE_SIZE` to `5` if you hit OOM errors.

### ❌ CORS errors from frontend

- Add your exact frontend URL to `CORS_ORIGINS`:
  ```
  CORS_ORIGINS=["https://your-app.vercel.app"]
  ```
- No trailing slash. Protocol (`https://`) required.
- Redeploy after updating.

### View logs

```bash
# Render: dashboard → Logs tab (real-time streaming)
# Railway:
railway logs --tail

# Docker:
docker logs yt-rag-chatbot -f
```
