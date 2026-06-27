"""
app.py — Streamlit front-end for the YouTube RAG Chatbot.

UI features
-----------
* Accepts full YouTube URLs **or** bare video IDs.
* Sidebar with project info, model badge, and a Clear Chat button.
* Chat-history display using st.chat_message.
* Expandable "Retrieved Context" panel per answer.
* Graceful, descriptive error handling for all known failure modes.
* Vector store cached per video ID — no redundant re-embedding.

LLM Provider: Google Gemini (ai.google.dev) — no local GPU required.
Transcript Provider: Supadata API (supadata.ai) — works on cloud platforms.
"""

import streamlit as st

from rag import build_vector_store, get_answer, extract_video_id, LLM_MODEL_NAME, GOOGLE_API_KEY, SUPADATA_API_KEY


# ── Page configuration ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube RAG Chatbot",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Global font & background ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(160deg, #0f0c29, #302b63, #24243e);
    }
    [data-testid="stSidebar"] * {
        color: #e0e0ff !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #c9b8ff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #555 !important;
    }

    /* ── Main content card feel ── */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2rem;
        max-width: 860px;
    }

    /* ── Primary button ── */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6c63ff, #a78bfa);
        border: none;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        padding: 0.55rem 1.2rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.45);
    }

    /* ── Context expander ── */
    [data-testid="stExpander"] summary {
        font-size: 0.85rem;
        font-weight: 500;
        color: #9ca3af;
    }

    /* ── Divider ── */
    hr { border-color: #2d2d2d !important; }

    /* ── Chat bubbles tweak ── */
    [data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 0.4rem 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ── Session state initialisation ───────────────────────────────────────────────
def _init_session_state() -> None:
    """Initialise all session-state keys once per browser session."""
    if "chat_history" not in st.session_state:
        # Each entry: {"video_id": str, "question": str, "answer": str, "docs": list}
        st.session_state.chat_history = []
    if "current_video_id" not in st.session_state:
        st.session_state.current_video_id = ""


_init_session_state()


# ── Vector store cache ─────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def cached_vector_store(video_id: str):
    """
    Build and cache the FAISS vector store for a given *video_id*.

    The @st.cache_resource decorator persists the store across Streamlit
    reruns for the lifetime of the server process, keyed by video_id.
    Switching to a different video creates a new entry; re-asking on the
    same video reuses the existing one — no redundant embedding.
    """
    return build_vector_store(video_id)


# ── Sidebar ────────────────────────────────────────────────────────────────────
def render_sidebar() -> None:
    """Render the sidebar with project info, model status, and a clear-chat button."""
    with st.sidebar:
        st.markdown("## 🎬 YouTube RAG Chatbot")
        st.markdown(
            "Ask questions about **any YouTube video** using its URL or Video ID. "
            "The app fetches the transcript, builds a semantic index, and answers "
            "using **Groq Cloud LLM** — fast, free-tier, and fully cloud-deployable."
        )
        st.divider()

        st.markdown("### ⚙️ Tech Stack")
        st.markdown(
            "- 🔗 **LangChain** — RAG orchestration\n"
            "- 🗄️ **FAISS** — vector similarity search\n"
            "- 🤗 **all-MiniLM-L6-v2** — sentence embeddings\n"
            "- ⚡ **Groq Cloud** — ultra-fast LLM inference\n"
            "- 🎞️ **YouTube Transcript API** — transcript fetch\n"
            "- 🖥️ **Streamlit** — web UI"
        )
        st.divider()

        st.markdown("### 📋 Accepted Input Formats")
        st.code(
            "https://www.youtube.com/watch?v=Gfr50f6ZBvo\n"
            "https://youtu.be/Gfr50f6ZBvo\n"
            "Gfr50f6ZBvo",
            language="text",
        )
        st.divider()

        # ── API Key & Model status ─────────────────────────────────────────
        st.markdown("### ⚡ Gemini Status")
        if GOOGLE_API_KEY and GOOGLE_API_KEY not in ("your_google_api_key_here", ""):
            st.success(
                f"**API Key:** configured ✅\n\n"
                f"**Model:** `{LLM_MODEL_NAME}`",
                icon="⚡",
            )
        else:
            st.error(
                "**GOOGLE_API_KEY** is not set.\n\n"
                "Add it to `backend/.env`:\n\n"
                "```\nGOOGLE_API_KEY=AIzaSy...\n```\n\n"
                "Get a free key at [aistudio.google.com](https://aistudio.google.com/app/apikey)",
                icon="🔑",
            )
        if not SUPADATA_API_KEY or SUPADATA_API_KEY in ("your_supadata_api_key_here", ""):
            st.error(
                "**SUPADATA_API_KEY** is not set.\n\n"
                "Add it to `backend/.env`:\n\n"
                "```\nSUPADATA_API_KEY=your_key...\n```\n\n"
                "Get a free key at [dash.supadata.ai](https://dash.supadata.ai)",
                icon="🔑",
            )
        st.divider()

        # Clear chat history
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_video_id = ""
            st.rerun()

        st.divider()
        st.caption("Built by **Harshit Malviya**")


render_sidebar()


# ── Main header ────────────────────────────────────────────────────────────────
st.markdown("## 🎥 YouTube RAG Chatbot")
st.markdown(
    "Enter a YouTube URL or Video ID, then ask questions about the video content. "
    "Answers are grounded in the video transcript — powered by **Google Gemini** ⚡ "
    "with transcripts from **Supadata API**."
)
st.divider()


# ── Video input ────────────────────────────────────────────────────────────────
st.markdown("#### 🔗 YouTube Video")

col_input, col_badge = st.columns([4, 1])

with col_input:
    raw_video_input = st.text_input(
        label="YouTube URL or Video ID",
        placeholder="https://www.youtube.com/watch?v=Gfr50f6ZBvo  or  Gfr50f6ZBvo",
        help=(
            "Accepted formats:\n"
            "• https://www.youtube.com/watch?v=<id>\n"
            "• https://youtu.be/<id>\n"
            "• Bare 11-character video ID"
        ),
        label_visibility="collapsed",
    )

# Resolve + validate the video ID immediately for live feedback
resolved_video_id: str = ""
if raw_video_input.strip():
    try:
        resolved_video_id = extract_video_id(raw_video_input)
        with col_badge:
            st.success(f"`{resolved_video_id}`", icon="✅")
    except ValueError as exc:
        st.error(f"⚠️ **Invalid input:** {exc}", icon="🚫")

st.divider()


# ── Chat history display ───────────────────────────────────────────────────────
def render_chat_history() -> None:
    """Render all Q&A pairs stored in session state as chat bubbles."""
    if not st.session_state.chat_history:
        st.markdown(
            "<p style='color:#6b7280; text-align:center; padding: 2rem 0;'>"
            "💬 No conversation yet. Enter a video URL above and ask a question below."
            "</p>",
            unsafe_allow_html=True,
        )
        return

    for entry in st.session_state.chat_history:
        # ── User bubble ───────────────────────────────────────────────────
        with st.chat_message("user"):
            st.markdown(
                f"<span style='font-size:0.78rem; color:#9ca3af;'>Video ID: "
                f"<code>{entry['video_id']}</code></span>",
                unsafe_allow_html=True,
            )
            st.markdown(entry["question"])

        # ── Assistant bubble ──────────────────────────────────────────────
      # ── Step 1 : Vector store ───────────────────────────────────────────────
    with st.spinner("⚙️ Fetching transcript via Supadata and building vector store…"):
        try:
            vector_store = cached_vector_store(video_id)
        except (ValueError, RuntimeError) as exc:
            err = str(exc)
            if "no transcript" in err.lower() or "empty transcript" in err.lower():
                st.error(
                    "❌ **No transcript found** for this video.\n\n"
                    "The video may not have captions, may be private, or may be unavailable. "
                    "Try a different public YouTube video with captions enabled.",
                    icon="🚫",
                )
            elif "supadata" in err.lower() or "api" in err.lower():
                st.error(
                    f"❌ **Supadata API error:**\n\n`{exc}`\n\n"
                    "Please check your SUPADATA_API_KEY and try again.",
                    icon="🚫",
                )
            else:
                st.error(
                    f"❌ **Could not fetch the transcript:**\n\n`{exc}`\n\n"
                    "Double-check the video ID and make sure the video is publicly accessible.",
                    icon="🚫",
                )
            return
        except Exception as exc:
            st.error(
                f"❌ **Could not fetch the transcript:**\n\n`{exc}`\n\n"
                "Double-check the video ID and make sure the video is publicly accessible.",
                icon="🚫",
            )
            return

    # ── Step 2 : Answer generation via Gemini ─────────────────────────────
    with st.spinner(f"⚡ Generating answer with Gemini `{LLM_MODEL_NAME}`…"):
        try:
            answer, retrieved_docs = get_answer(question, vector_store)
        except EnvironmentError as exc:
            st.error(
                f"❌ **API Key Error:**\n\n{exc}",
                icon="🔑",
            )
            return
        except Exception as exc:
            error_msg = str(exc)
            # Provide specific guidance for common Gemini errors
            if "rate_limit" in error_msg.lower() or "429" in error_msg:
                st.error(
                    "❌ **Gemini Rate Limit Exceeded.**\n\n"
                    "Wait 60 seconds, then try again. "
                    "Consider switching to `gemini-2.5-flash` for higher rate limits.",
                    icon="⏳",
                )
            elif "invalid" in error_msg.lower() and "key" in error_msg.lower() or "401" in error_msg:
                st.error(
                    "❌ **Invalid Google API Key.**\n\n"
                    "Check `GOOGLE_API_KEY` in `backend/.env`. "
                    "Get a valid key at [aistudio.google.com](https://aistudio.google.com/app/apikey)",
                    icon="🔑",
                )
            elif any(kw in error_msg.lower() for kw in ("connect", "network", "timeout")):
                st.error(
                    "❌ **Cannot reach Gemini API.**\n\n"
                    "Check your internet connection. "
                    "The Gemini API endpoint is `generativelanguage.googleapis.com`.",
                    icon="🌐",
                )
            else:
                st.error(
                    f"❌ **Error generating answer:**\n\n`{exc}`",
                    icon="🚫",
                )
            return

    # ── Step 3 : Persist in session state ────────────────────────────────
    st.session_state.chat_history.append(
        {
            "video_id": video_id,
            "question": question,
            "answer":   answer,
            "docs":     retrieved_docs,
        }
    )
    st.session_state.current_video_id = video_id

    # ── Step 4 : Rerun to refresh the chat display ────────────────────────
    st.rerun()


if user_question:
    if not resolved_video_id:
        # Defensive check — the input is disabled when no valid ID is set,
        # but handle the edge-case where someone pastes a question anyway.
        st.error("⚠️ Please enter a valid YouTube URL or Video ID first.", icon="⚠️")
    else:
        process_question(resolved_video_id, user_question.strip())