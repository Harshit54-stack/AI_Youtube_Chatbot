"""
run.py — Convenience launcher for the YouTube RAG Chatbot backend.

Run from the project root (d:/AI_Youtube_Chatbot):
    python run.py

This is equivalent to:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # auto-restart on code changes (development mode)
        log_level="info",
    )
