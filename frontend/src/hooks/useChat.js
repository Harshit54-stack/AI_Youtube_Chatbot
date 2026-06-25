/**
 * useChat.js — Custom hook managing the entire chat session state.
 *
 * Responsibilities:
 *  - Store message history in state (and sync to localStorage)
 *  - Manage current video URL (synced to localStorage)
 *  - Handle API calls and loading / error states
 *  - Expose actions: sendMessage, clearChat, setVideoUrl
 */
import { useState, useEffect, useCallback, useRef } from 'react'
import { askQuestion, checkHealth } from '../services/api'

const STORAGE_KEY_MESSAGES  = 'yt_rag_messages'
const STORAGE_KEY_VIDEO_URL = 'yt_rag_video_url'

// ── Helpers ──────────────────────────────────────────────────────────────────

const loadFromStorage = (key, fallback) => {
  try {
    const raw = localStorage.getItem(key)
    return raw ? JSON.parse(raw) : fallback
  } catch {
    return fallback
  }
}

const saveToStorage = (key, value) => {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch {}
}

// ── YouTube URL validation ────────────────────────────────────────────────────

export const isValidYouTubeUrl = (url) => {
  if (!url || !url.trim()) return false
  const patterns = [
    /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]{11}/,
    /^https?:\/\/youtu\.be\/[\w-]{11}/,
    /^https?:\/\/(www\.)?youtube\.com\/shorts\/[\w-]{11}/,
    /^[\w-]{11}$/, // bare video ID
  ]
  return patterns.some((p) => p.test(url.trim()))
}

// ── Hook ──────────────────────────────────────────────────────────────────────

export const useChat = () => {
  const [messages,  setMessages]  = useState(() => loadFromStorage(STORAGE_KEY_MESSAGES, []))
  const [videoUrl,  setVideoUrlState] = useState(() => loadFromStorage(STORAGE_KEY_VIDEO_URL, ''))
  const [isLoading, setIsLoading] = useState(false)
  const [error,     setError]     = useState(null)
  const [backendStatus, setBackendStatus] = useState('unknown') // 'ok' | 'error' | 'unknown'

  const abortRef = useRef(null)

  // ── Persist messages ───────────────────────────────────────────────────────
  useEffect(() => { saveToStorage(STORAGE_KEY_MESSAGES, messages) }, [messages])

  // ── Persist video URL ──────────────────────────────────────────────────────
  const setVideoUrl = useCallback((url) => {
    setVideoUrlState(url)
    saveToStorage(STORAGE_KEY_VIDEO_URL, url)
  }, [])

  // ── Health check on mount ──────────────────────────────────────────────────
  useEffect(() => {
    let cancelled = false
    const ping = async () => {
      try {
        await checkHealth()
        if (!cancelled) setBackendStatus('ok')
      } catch {
        if (!cancelled) setBackendStatus('error')
      }
    }
    ping()
    return () => { cancelled = true }
  }, [])

  // ── Send message ───────────────────────────────────────────────────────────
  const sendMessage = useCallback(async (question) => {
    if (!question.trim()) {
      setError('Please enter a question.')
      return
    }
    if (!isValidYouTubeUrl(videoUrl)) {
      setError('Please enter a valid YouTube URL in the sidebar.')
      return
    }

    setError(null)
    setIsLoading(true)

    // Add the user bubble immediately
    const userMessage = {
      id:        crypto.randomUUID(),
      role:      'user',
      content:   question.trim(),
      timestamp: Date.now(),
    }
    setMessages((prev) => [...prev, userMessage])

    try {
      const data = await askQuestion(videoUrl, question.trim())

      const aiMessage = {
        id:        crypto.randomUUID(),
        role:      'assistant',
        content:   data.answer,
        sources:   data.sources || [],
        videoId:   data.video_id,
        timestamp: Date.now(),
        raw_data:  data, // Inject raw data for debugging
      }
      setMessages((prev) => [...prev, aiMessage])
    } catch (err) {
      const aiError = {
        id:        crypto.randomUUID(),
        role:      'assistant',
        content:   null,
        error:     err.message || 'Something went wrong. Please try again.',
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, aiError])
      setError(err.message || 'Request failed.')
    } finally {
      setIsLoading(false)
    }
  }, [videoUrl])

  // ── Clear chat ─────────────────────────────────────────────────────────────
  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
    localStorage.removeItem(STORAGE_KEY_MESSAGES)
  }, [])

  return {
    messages,
    videoUrl,
    setVideoUrl,
    isLoading,
    error,
    setError,
    backendStatus,
    sendMessage,
    clearChat,
  }
}
