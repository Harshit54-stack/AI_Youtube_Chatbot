# 🎬 YouTube RAG Chatbot

An AI-powered YouTube RAG Chatbot built with React, FastAPI, LangChain, FAISS, HuggingFace Embeddings, YouTube Transcript API, and Google Gemini.

* Google Gemini is the LLM provider.
* Gemini generates answers from retrieved context.
* Gemini is used for conversational reasoning.

---

## ✨ Features

| Feature | Details |
|---|---|
| **YouTube URL support** | Accepts full URLs (`youtube.com/watch?v=…`, `youtu.be/…`) or bare Video IDs |
| **Google Gemini LLM** | Ultra-fast inference via `gemini-1.5-flash` or any Gemini model |
| **Anti-hallucination prompts** | System + Human chat template; LLM strictly answers from transcript only |
| **Multi-model support** | Switch between Gemini 1.5 Pro, Gemini 1.5 Flash via `.env` |
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
│ React Frontend │                                                    │
│ RAG Pipeline   │  POST /ask          GET /health      GET /models   │
│ Google Gemini  │                                                    │
└────────┬───────┴──────────────────┬───────────────────────────────-─┘
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RAG Pipeline                               │
│                                                                     │
│  YouTube URL/ID                                                     │
│       │                                                             │
│       ▼                                                             │
│  extract_video_id()   ← URL parsing + validation                    │
│       │                                                             │
│       ▼                                                             │
│  YouTubeTranscriptApi ← Fetch English transcript                    │
│       │                                                             │
│       ▼                                                             │
│  RecursiveCharacterTextSplitter  ← chunk_size=1000, overlap=200     │
│       │                                                             │
│       ▼                                                             │
│  HuggingFaceEmbeddings           ← all-MiniLM-L6-v2 (local, free)   │
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
│  ChatGoogleGenerativeAI (Google Gemini ⚡) ← gemini-1.5-flash (default) 
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
    ├── requirements.txt            # Production deps (FastAPI + Gemini)
    ├── .env                        # Your secrets (gitignored)
    ├── .env.example                # Template — copy to .env
    │
    ├── services/
    │   ├── transcript_service.py   # YouTube transcript fetch + splitting
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
- A free Google Gemini API key → [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

### 1. Clone & install dependencies

```bash
git clone https://github.com/your-username/AI_Youtube_Chatbot.git
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

# Optional — defaults shown
LLM_MODEL_NAME=gemini-1.5-flash
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

Ask a question about a YouTube video.

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
  "llm_model": "gemini-1.5-flash"
}
```

### `GET /models`

Returns the full catalogue of supported Gemini models with metadata.


## ⚙️ Configuration Reference

All settings are read from `backend/.env` (or OS environment variables):

| Variable | Default | Description |
|---|---|---|
| `GOOGLE_API_KEY` | **required** | Google Gemini API key |
| `LLM_MODEL_NAME` | `gemini-1.5-flash` | Gemini model ID |
| `LLM_TEMPERATURE` | `0.0` | Sampling temp (0=deterministic) |
| `LLM_MAX_TOKENS` | `1024` | Max tokens per response |
| `LLM_TIMEOUT` | `60` | API timeout in seconds |
| `LLM_MAX_RETRIES` | `2` | Auto-retries on transient errors |
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | HuggingFace embedding model |
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

# Run (pass API key as env var)
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=AIzaSy... \
  -e LLM_MODEL_NAME=gemini-1.5-flash \
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
4. Set `GOOGLE_API_KEY` in the Render dashboard (Environment tab)
5. Deploy ✅

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variable
railway variables set GOOGLE_API_KEY=AIzaSy...
```

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for step-by-step guides for both platforms.

---

## 🔄 Migration: Ollama → Gemini

| | Phase 2 (Ollama) | Phase 3 (Gemini) |
|---|---|---|
| **LLM Provider** | Local Ollama | Google Gemini API |
| **Deployment** | Local only | Any cloud platform |
| **GPU required** | Yes (for speed) | No |
| **Setup** | Install Ollama + pull model | Set one env var |
| **Cold start** | ~30s model load | <1s |
| **Inference speed** | ~20-50 tok/s (CPU) | ~300-800 tok/s |
| **Cost** | Free (local compute) | Free tier generous |
| **Scalability** | Single machine | Horizontal |
| **Model switching** | Pull new model | Change env var |
| **CI/CD friendly** | ❌ | ✅ |

---

## 🧰 Error Handling

The API returns structured JSON errors for all failure modes:

```json
{
  "error": "LLM_CONNECTION_ERROR",
  "detail": "Cannot reach the Google Gemini API. Check your internet connection.",
  "status_code": 503
}
```

| Error Code | HTTP | Cause |
|---|---|---|
| `INVALID_VIDEO_URL` | 422 | Bad YouTube URL or video ID |
| `TRANSCRIPT_DISABLED` | 422 | Video creator disabled captions |
| `TRANSCRIPT_NOT_FOUND` | 404 | No English transcript available |
| `VECTOR_STORE_ERROR` | 500 | FAISS build or search failure |
| `LLM_CONNECTION_ERROR` | 503 | Gemini unreachable / invalid API key / timeout |
| `LLM_GENERATION_ERROR` | 500 | Rate limit / bad model / empty response |

---

## 🗺️ Roadmap

- [x] Phase 1 — Streamlit prototype + Ollama
- [x] Phase 2 — FastAPI backend + service architecture
- [x] Phase 3 — Google Gemini migration + deployment config
- [x] Phase 4 — React frontend (Next.js / Vite)
- [x] Phase 5 — Persistent vector store (Redis / Pinecone)
- [x] Phase 6 — Auth + multi-user support

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
