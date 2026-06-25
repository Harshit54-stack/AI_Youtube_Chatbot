# VideoMind — Frontend

> React + Vite + Tailwind CSS v4 frontend for the YouTube RAG Chatbot.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | ≥ 18 |
| npm | ≥ 9 |
| FastAPI backend | running on port 8000 |

---

## Local Setup

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Configure environment
cp .env.example .env
# Default: VITE_API_URL=http://localhost:8000

# 3. Start dev server
npm run dev
# → http://localhost:5173
```

Make sure your FastAPI backend is running first:
```bash
# From project root
python run.py
# → http://localhost:8000
```

---

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Navbar.jsx        # Top bar — brand, backend status, model badge
│   │   ├── Sidebar.jsx       # Video URL input, thumbnail preview, clear chat
│   │   ├── ChatBox.jsx       # Conversation list + welcome screen
│   │   ├── Message.jsx       # User / AI chat bubbles with copy button
│   │   ├── SourcesPanel.jsx  # Collapsible transcript chunk citations
│   │   ├── Loader.jsx        # Animated typing indicator
│   │   └── Footer.jsx        # Auto-resize question input + send button
│   ├── hooks/
│   │   └── useChat.js        # All state: messages, URL, loading, localStorage
│   ├── pages/
│   │   └── Home.jsx          # Layout — assembles all components
│   ├── services/
│   │   └── api.js            # Axios layer — askQuestion, checkHealth, listModels
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css             # Design tokens + Tailwind v4 + global styles
├── .env                      # VITE_API_URL
├── .env.example
├── vite.config.js            # Vite + Tailwind v4 plugin + dev proxy
├── vercel.json               # SPA routing for Vercel
├── netlify.toml              # SPA routing for Netlify
└── index.html                # SEO meta, Google Fonts, favicon
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start dev server at localhost:5173 |
| `npm run build` | Production build → `dist/` |
| `npm run preview` | Preview production build locally |

---

## Features

- 🎥 **YouTube URL input** with real-time validation and thumbnail preview
- 💬 **Chat interface** — user bubbles right, AI bubbles left
- 📚 **Source citations** — expand/collapse retrieved transcript chunks
- ⚡ **Groq-powered** — near-instant AI responses via LLaMA 3
- 🔄 **Chat persistence** — messages and last video URL saved to `localStorage`
- 📋 **Copy button** — hover AI messages to copy the answer
- ❌ **Error handling** — invalid URL, API offline, empty question, backend errors
- 🌐 **Backend status badge** — live health check on load
- 📱 **Responsive** — mobile sidebar slide-in, desktop full layout
- 🔒 **Grounded answers** — no hallucinations, sourced from transcript only

---

## Deployment

### Vercel
```bash
# From project root
vercel --cwd frontend

# Set environment variable in Vercel dashboard:
# VITE_API_URL = https://your-backend.onrender.com
```

### Netlify
```bash
# Build settings in Netlify dashboard:
# Base directory:   frontend
# Build command:    npm run build
# Publish directory: frontend/dist

# Environment variable:
# VITE_API_URL = https://your-backend.onrender.com
```

> **Note**: Your FastAPI backend must have CORS configured for your deployed frontend URL.
> Update `CORS_ORIGINS` in `backend/.env`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + Vite 8 |
| Styling | Tailwind CSS v4 + Custom CSS tokens |
| HTTP | Axios with interceptors |
| State | React Hooks (`useState`, `useEffect`, `useCallback`) |
| Persistence | `localStorage` |
| Icons | Lucide React |
| Fonts | Inter + JetBrains Mono (Google Fonts) |
