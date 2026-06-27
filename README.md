# 🎬 YouTube RAG Chatbot

An AI-powered YouTube RAG Chatbot built with React, FastAPI, LangChain, FAISS,
Google Generative AI Embeddings, **Supadata Transcript API**, and Google Gemini.

- Google Gemini is the LLM provider.
- Gemini generates answers from retrieved context.
- Supadata fetches transcripts reliably on all cloud platforms.

---

## ✨ Features

| Feature | Details |
|---|---|
| **YouTube URL support** | Accepts full URLs (`youtube.com/watch?v=…`, `youtu.be/…`) or bare Video IDs |
| **Supadata Transcript API** | Cloud-friendly transcript fetching — works on Render without IP-blocking |
| **Google Gemini LLM** | Ultra-fast inference via `gemini-2.5-flash` or any Gemini model |
| **Anti-hallucination prompts** | System + Human chat template; LLM strictly answers from transcript only |
| **Multi-model support** | Switch between Gemini 2.5 Flash, 2.5 Pro, 2.0 Flash, 1.5 Flash via `.env` |
| **FastAPI backend** | Production-grade REST API with Swagger UI at `/docs` |
| **Chat history** | Full conversation history preserved within the browser session |
| **Retrieved context** | Expandable panel shows the exact transcript chunks used per answer |
| **Smart LRU caching** | Vector store built once per video; reused across all follow-up questions |
| **Structured logging** | ISO-8601 timestamps, request IDs, token usage per Gemini response |
| **Docker + Render ready** | Multi-stage Dockerfile, `render.yaml` blueprint included |
| **Environment-driven config** | All settings via `.env` — zero hardcoded secrets |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YouTube RAG Chatbot                         │
├────────────────┬────────────────────────────────────────────────────┤
│ React Frontend │            FastAPI Backend (production)            │
│                │                                                    │
│                │  POST /ask          GET /health      GET /models   │
│                │                                                    │
└────────┬───────┴──────────────────┬─────────────────────────────────┘
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RAG Pipeline                               │
│                                                                     │
│  YouTube URL/ID                                                     │
│       │                                                             │
│       ▼                                                             │
│  extract_video_id()        ← URL parsing + validation               │
│       │                                                             │
│       ▼                                                             │
│  Supadata Transcript API   ← Cloud-friendly, no IP-blocking         │
│  (api.supadata.ai)           Works reliably on Render & Railway     │
│       │                                                             │
│       ▼                                                             │
│  RecursiveCharacterTextSplitter  ← chunk_size=1000, overlap=200     │
│       │                                                             │
│       ▼                                                             │
│  GoogleGenerativeAIEmbeddings    ← models/gemini-embedding-2        │
│       │                                                             │
│       ▼                                                             │
│  FAISS.from_documents()          ← In-memory index (LRU cache)      │
│       │                                                             │
│       ▼                                                             │
│  similarity_search(k=4)          ← Top-4 relevant chunks            │
│       │                                                             │
│       ▼                                                             │
│  System + Human Prompt           ← Anti-hallucination template      │
│       │                                                             │
│       ▼                                                             │
│  ChatGoogleGenerativeAI (Gemini ⚡) ← gemini-2.5-flash (default)   │
└─────────────────────────────────────────────────────────────────────┘
```

### Backend Directory Structure

```
AI_Youtube_Chatbot/
├── app.py                          # Streamlit prototype UI
├── rag.py                          # Streamlit RAG pipeline (Gemini-powered)
├── run.py                          # FastAPI dev server launcher
├── requirements.txt                # Root deps (Streamlit prototype)
├── Dockerfile                      # Multi-stage production Docker build
├── render.yaml                     # Render.com deployment blueprint
│
└── backend/                        # Production FastAPI application
    ├── main.py                     # FastAPI app, routes, middleware
    ├── config.py                   # Centralised settings (pydantic-settings)
    ├── rag.py                      # RAGService orchestration facade
    ├── requirements.txt            # Production deps (FastAPI + Gemini + Supadata)
    ├── .env                        # Your secrets (gitignored)
    ├── .env.example                # Template — copy to .env
    │
    ├── services/
    │   ├── transcript_service.py   # Supadata transcript fetch + text splitting
    │   ├── vector_store_service.py # FAISS build + LRU cache
    │   ├── retrieval_service.py    # Similarity search
    │   └── llm_service.py         # ChatGoogleGenerativeAI client + error handling
    │
    ├── models/
    │   ├── request_models.py       # Pydantic request schemas
    │   └── response_models.py      # Pydantic response schemas
    │
    └── utils/
        ├── exceptions.py           # Custom exception hierarchy
        └── logger.py               # Structured logger factory
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- A free **Google Gemini API key** → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- A free **Supadata API key** → [dash.supadata.ai](https://dash.supadata.ai)

### 1. Clone & install dependencies

```bash
git clone https://github.com/Harshit54-stack/AI_Youtube_Chatbot.git
cd AI_Youtube_Chatbot

# For FastAPI backend (recommended):
pip install -r backend/requirements.txt

# For Streamlit prototype only:
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# Required
GOOGLE_API_KEY=AIzaSy...
SUPADATA_API_KEY=your_supadata_key_here

# Optional — defaults shown
LLM_MODEL_NAME=gemini-2.5-flash
LLM_TEMPERATURE=0.0
LLM_MAX_TOKENS=1024
```

### 3a. Run the FastAPI backend

```bash
python run.py
```

API available at:
- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc
- **Health** → http://localhost:8000/health

### 3b. Run the Streamlit prototype

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 🔌 API Reference

### `POST /ask`

Ask a question about a YouTube video. Transcript is retrieved using **Supadata API**.

**Request:**
```json
{
  "video_url": "https://www.youtube.com/watch?v=Gfr50f6ZBvo",
  "question": "What is the main topic of this video?"
}
```

**Response:**
```json
{
  "video_id": "Gfr50f6ZBvo",
  "question": "What is the main topic of this video?",
  "answer": "The video covers...",
  "sources": [
    { "chunk_index": 1, "content": "...transcript excerpt..." },
    { "chunk_index": 2, "content": "...transcript excerpt..." }
  ]
}
```

### `GET /health`

```json
{
  "status": "ok",
  "api": "YouTube RAG Chatbot",
  "version": "3.0.0",
  "environment": "production",
  "llm_provider": "Google Gemini",
  "llm_model": "gemini-2.5-flash"
}
```

### `GET /models`

Returns the full catalogue of supported Gemini models with metadata.

---

## 🤖 Supported Gemini Models

| Model ID | Context | Speed | Quality |
|---|---|---|---|
| `gemini-2.5-flash` | 1M | ⚡ Fast | ⭐ Highest (default) |
| `gemini-2.5-pro` | 1M | Medium | ⭐ Highest |
| `gemini-2.0-flash` | 1M | ⚡ Fastest | High |
| `gemini-2.0-flash-lite` | 1M | ⚡ Fastest | Good |
| `gemini-1.5-flash` | 1M | ⚡ Fast | High |
| `gemini-1.5-flash-8b` | 1M | ⚡ Fastest | Good |
| `gemini-1.5-pro` | 2M | Medium | ⭐ Highest |

Switch models by setting `LLM_MODEL_NAME` in `backend/.env` and restarting the server.

---

## ⚙️ Configuration Reference

All settings are read from `backend/.env` (or OS environment variables):

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | **required** | Google Gemini API key |
| `SUPADATA_API_KEY` | **required** | Supadata Transcript API key |
| `LLM_MODEL_NAME` | `gemini-2.5-flash` | Gemini model ID |
| `LLM_TEMPERATURE` | `0.0` | Sampling temp (0=deterministic) |
| `LLM_MAX_TOKENS` | `1024` | Max tokens per response |
| `LLM_TIMEOUT` | `60` | API timeout in seconds |
| `LLM_MAX_RETRIES` | `2` | Auto-retries on transient errors |
| `EMBEDDING_MODEL_NAME` | `models/gemini-embedding-2` | Google embedding model |
| `CHUNK_SIZE` | `1000` | Characters per transcript chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between adjacent chunks |
| `RETRIEVER_K` | `4` | Chunks retrieved per question |
| `VECTOR_STORE_CACHE_SIZE` | `20` | Max cached video indexes (LRU) |
| `CORS_ORIGINS` | `["http://localhost:3000","http://localhost:5173"]` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR |
| `APP_ENV` | `development` | development \| staging \| production |

---

## 🐳 Docker

```bash
# Build
docker build -t yt-rag-chatbot .

# Run (pass API keys as env vars)
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=AIzaSy... \
  -e SUPADATA_API_KEY=your_supadata_key \
  -e LLM_MODEL_NAME=gemini-2.5-flash \
  yt-rag-chatbot

# Or mount your .env file
docker run -p 8000:8000 --env-file backend/.env yt-rag-chatbot
```

---

## ☁️ Deployment

### Render

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Select your repo — Render auto-detects `render.yaml`
4. Set **both** environment variables in the Render dashboard (Environment tab):
   - `GOOGLE_API_KEY` — from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
   - `SUPADATA_API_KEY` — from [dash.supadata.ai](https://dash.supadata.ai)
5. Deploy ✅

> **Why Supadata?** Render's shared IPs are blocked by YouTube's transcript scraping protection. Supadata routes transcript requests through its own infrastructure, eliminating this problem entirely.

### Vercel (Frontend)

The React frontend deploys to Vercel with no additional configuration. Set the `VITE_API_URL` environment variable in Vercel to point to your Render backend URL.

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for step-by-step guides for Render, Railway, and Docker.

---

## 🧰 Error Handling

The API returns structured JSON errors for all failure modes:

```json
{
  "error": "SUPADATA_API_ERROR",
  "detail": "The request to Supadata timed out. Please try again.",
  "status_code": 502
}
```

| Error Code | HTTP | Cause |
|---|---|---|
| `INVALID_VIDEO_URL` | 422 | Bad YouTube URL or video ID |
| `TRANSCRIPT_DISABLED` | 422 | Video creator disabled captions |
| `TRANSCRIPT_NOT_FOUND` | 404 | No transcript available for the video |
| `SUPADATA_API_ERROR` | 502 | Supadata unreachable / timeout / unexpected error |
| `VECTOR_STORE_ERROR` | 500 | FAISS build or search failure |
| `LLM_CONNECTION_ERROR` | 503 | Gemini unreachable / invalid API key / timeout |
| `LLM_GENERATION_ERROR` | 500 | Rate limit / bad model / empty response |

---

## 🗺️ Roadmap

- [x] Phase 1 — Streamlit prototype + Ollama
- [x] Phase 2 — FastAPI backend + service architecture
- [x] Phase 3 — Google Gemini migration + deployment config
- [x] Phase 4 — React frontend (Vite)
- [x] Phase 5 — Supadata integration (cloud-ready transcript fetching)

---

## 👤 Author

Harshit Malviya

Aspiring AI/ML Engineer passionate about:
- Generative AI
- RAG Systems
- LLM Applications
- Full-Stack AI Development

GitHub: https://github.com/Harshit54-stack
LinkedIn: www.linkedin.com/in/harshit-malviya-0422a4324
