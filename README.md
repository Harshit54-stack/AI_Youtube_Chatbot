# 🎬 YouTube RAG Chatbot — Phase 3 (Groq Cloud)

A production-ready **Retrieval-Augmented Generation (RAG)** chatbot that answers questions about any YouTube video using its transcript. Powered by **Groq Cloud** for ultra-fast LLM inference — no local GPU, no Ollama, fully cloud-deployable.

---

## ✨ Features

| Feature | Details |
|---|---|
| **YouTube URL support** | Accepts full URLs (`youtube.com/watch?v=…`, `youtu.be/…`) or bare Video IDs |
| **Groq Cloud LLM** | Ultra-fast inference via `llama-3.1-8b-instant` or any Groq model |
| **Anti-hallucination prompts** | System + Human chat template; LLM strictly answers from transcript only |
| **Multi-model support** | Switch between LLaMA 3.3 70B, LLaMA 3.1 8B, Gemma 2, Mixtral via `.env` |
| **FastAPI backend** | Production-grade REST API with Swagger UI at `/docs` |
| **Chat history** | Full conversation history preserved within the browser session |
| **Retrieved context** | Expandable panel shows the exact transcript chunks used per answer |
| **Smart LRU caching** | Vector store built once per video; reused across all follow-up questions |
| **Structured logging** | ISO-8601 timestamps, request IDs, token usage per Groq response |
| **Docker + Render ready** | Multi-stage Dockerfile, `render.yaml` blueprint included |
| **Environment-driven config** | All settings via `.env` — zero hardcoded secrets |

---

## 🏗️ Architecture

### Phase 3 — Groq Cloud (Current)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         YouTube RAG Chatbot                         │
├────────────────┬────────────────────────────────────────────────────┤
│  Streamlit UI  │            FastAPI Backend (production)            │
│   (prototype)  │                                                    │
│   app.py       │  POST /ask          GET /health      GET /models   │
│   rag.py       │       │                                            │
└────────┬───────┴──────────────────┬───────────────────────────────-─┘
         │                          │
         ▼                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          RAG Pipeline                               │
│                                                                     │
│  YouTube URL/ID                                                     │
│       │                                                             │
│       ▼                                                             │
│  extract_video_id()   ← URL parsing + validation                   │
│       │                                                             │
│       ▼                                                             │
│  YouTubeTranscriptApi ← Fetch English transcript                   │
│       │                                                             │
│       ▼                                                             │
│  RecursiveCharacterTextSplitter  ← chunk_size=1000, overlap=200    │
│       │                                                             │
│       ▼                                                             │
│  HuggingFaceEmbeddings           ← all-MiniLM-L6-v2 (local, free) │
│       │                                                             │
│       ▼                                                             │
│  FAISS.from_documents()          ← In-memory index (LRU cache)     │
│       │                                                             │
│       ▼                                                             │
│  similarity_search(k=4)          ← Top-4 relevant chunks           │
│       │                                                             │
│       ▼                                                             │
│  System + Human Prompt           ← Anti-hallucination template     │
│       │                                                             │
│       ▼                                                             │
│  ChatGroq (Groq Cloud ⚡)        ← llama-3.1-8b-instant (default) │
└─────────────────────────────────────────────────────────────────────┘
```

### Backend Directory Structure

```
AI_Youtube_Chatbot/
├── app.py                          # Streamlit prototype UI
├── rag.py                          # Streamlit RAG pipeline (Groq-powered)
├── run.py                          # FastAPI dev server launcher
├── requirements.txt                # Root deps (Streamlit prototype)
├── Dockerfile                      # Multi-stage production Docker build
├── render.yaml                     # Render.com deployment blueprint
│
└── backend/                        # Production FastAPI application
    ├── main.py                     # FastAPI app, routes, middleware
    ├── config.py                   # Centralised settings (pydantic-settings)
    ├── rag.py                      # RAGService orchestration facade
    ├── requirements.txt            # Production deps (FastAPI + Groq)
    ├── .env                        # Your secrets (gitignored)
    ├── .env.example                # Template — copy to .env
    │
    ├── services/
    │   ├── transcript_service.py   # YouTube transcript fetch + splitting
    │   ├── vector_store_service.py # FAISS build + LRU cache
    │   ├── retrieval_service.py    # Similarity search
    │   └── llm_service.py         # ChatGroq client + error handling
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
- A free Groq API key → [console.groq.com](https://console.groq.com)

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
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional — defaults shown
LLM_MODEL_NAME=llama-3.1-8b-instant
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
  "llm_provider": "Groq Cloud",
  "llm_model": "llama-3.1-8b-instant"
}
```

### `GET /models`

Returns the full catalogue of supported Groq models with metadata.

---

## 🤖 Supported Groq Models

| Model ID | Params | Context | Speed | Quality |
|---|---|---|---|---|
| `llama-3.1-8b-instant` | 8B | 128k | ⚡ Fastest | Good |
| `llama-3.3-70b-versatile` | 70B | 128k | Medium | ⭐ Best |
| `llama3-8b-8192` | 8B | 8k | Fast | Good |
| `llama3-70b-8192` | 70B | 8k | Medium | High |
| `gemma2-9b-it` | 9B | 8k | Fast | Good |
| `gemma-7b-it` | 7B | 8k | Fast | Good |
| `mixtral-8x7b-32768` | 47B (MoE) | 32k | Medium | High |

Switch models by setting `LLM_MODEL_NAME` in `backend/.env` and restarting the server.

---

## ⚙️ Configuration Reference

All settings are read from `backend/.env` (or OS environment variables):

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | **required** | Groq Cloud API key |
| `LLM_MODEL_NAME` | `llama-3.1-8b-instant` | Groq model ID |
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
  -e GROQ_API_KEY=gsk_xxx \
  -e LLM_MODEL_NAME=llama-3.1-8b-instant \
  yt-rag-chatbot

# Or mount your .env file
docker run -p 8000:8000 --env-file backend/.env yt-rag-chatbot
```

---

## ☁️ Deployment

### Render (recommended)

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint**
3. Select your repo — Render auto-detects `render.yaml`
4. Set `GROQ_API_KEY` in the Render dashboard (Environment tab)
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
railway variables set GROQ_API_KEY=gsk_xxx
```

See [`DEPLOYMENT.md`](./DEPLOYMENT.md) for step-by-step guides for both platforms.

---

## 🔄 Migration: Ollama → Groq

| | Phase 2 (Ollama) | Phase 3 (Groq) |
|---|---|---|
| **LLM Provider** | Local Ollama | Groq Cloud API |
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
  "detail": "Cannot reach the Groq API. Check your internet connection.",
  "status_code": 503
}
```

| Error Code | HTTP | Cause |
|---|---|---|
| `INVALID_VIDEO_URL` | 422 | Bad YouTube URL or video ID |
| `TRANSCRIPT_DISABLED` | 422 | Video creator disabled captions |
| `TRANSCRIPT_NOT_FOUND` | 404 | No English transcript available |
| `VECTOR_STORE_ERROR` | 500 | FAISS build or search failure |
| `LLM_CONNECTION_ERROR` | 503 | Groq unreachable / invalid API key / timeout |
| `LLM_GENERATION_ERROR` | 500 | Rate limit / bad model / empty response |

---

## 🗺️ Roadmap

- [x] Phase 1 — Streamlit prototype + Ollama
- [x] Phase 2 — FastAPI backend + service architecture
- [x] Phase 3 — Groq Cloud migration + deployment config
- [ ] Phase 4 — React frontend (Next.js / Vite)
- [ ] Phase 5 — Persistent vector store (Redis / Pinecone)
- [ ] Phase 6 — Auth + multi-user support

---

## 👤 Author

**Harshit Malviya**
