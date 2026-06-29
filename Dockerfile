# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile — YouTube RAG Chatbot Backend
#
# Multi-stage build:
#   Stage 1 (builder) : Install Python deps into a venv
#   Stage 2 (runtime) : Slim image with only the venv + app code
#
# Build:
#   docker build -t yt-rag-chatbot .
#
# Run:
#   docker run -p 8000:8000 \
#     -e GOOGLE_API_KEY=AIzaSy... \
#     -e LLM_MODEL_NAME=gemini-1.5-flash \
#     yt-rag-chatbot
#
# Or with a .env file:
#   docker run -p 8000:8000 --env-file backend/.env yt-rag-chatbot
# ─────────────────────────────────────────────────────────────────────────────

# ── Stage 1: Dependency builder ───────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools needed for some Python packages (e.g. faiss-cpu)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate deps
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install only the dependency file first (Docker layer caching)
COPY backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Production runtime ───────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Security: run as non-root user
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY backend/ ./backend/
#COPY run.py ./run.py

# Ensure the app directory is owned by appuser
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# ── Runtime configuration ──────────────────────────────────────────────────────
# PORT is set by Render/Railway automatically; default 8000 for local Docker
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE $PORT

# Health check — Render/Railway use this to know when the container is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import httpx; httpx.get(f'http://localhost:{PORT}/health').raise_for_status()" \
    || exit 1

# Start the FastAPI server
# --workers 1: single worker is safe because HuggingFace embeddings are shared
# --host 0.0.0.0: required for Docker networking
CMD uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port $PORT \
    --workers 1 \
    --log-level info \
    --access-log
