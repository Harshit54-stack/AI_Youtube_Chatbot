/**
 * api.js — Axios service layer for the YouTube RAG Chatbot API.
 *
 * All communication with the FastAPI backend goes through this module.
 * The base URL is controlled by the VITE_API_URL environment variable.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 120_000, // 2 minutes — RAG can take time on first video load
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Request interceptor ──────────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

// ── Response interceptor ─────────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalize error shape so components always deal with a { message, code } object
    const status = error.response?.status
    const detail = error.response?.data?.detail || error.message || 'Unknown error'
    const code   = error.response?.data?.error  || 'NETWORK_ERROR'

    const normalized = {
      message: detail,
      code,
      status,
    }

    return Promise.reject(normalized)
  },
)

// ── API functions ────────────────────────────────────────────────────────────

/**
 * POST /ask — Send a question about a YouTube video.
 * @param {string} videoUrl - Full YouTube URL
 * @param {string} question - User's question
 * @returns {Promise<{ video_id: string, question: string, answer: string, sources: Array }>}
 */
export const askQuestion = async (videoUrl, question) => {
  const response = await apiClient.post('/ask', {
    video_url: videoUrl,
    question,
  })
  return response.data
}

/**
 * GET /health — Check if the backend is running.
 * @returns {Promise<{ status: string, llm_model: string, environment: string }>}
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health')
  return response.data
}

/**
 * GET /models — List all supported Groq models.
 * @returns {Promise<{ active_model: string, supported_models: Array }>}
 */
export const listModels = async () => {
  const response = await apiClient.get('/models')
  return response.data
}

export default apiClient
