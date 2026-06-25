/**
 * ChatBox.jsx — Scrollable conversation history container.
 *
 * Handles:
 *  - Auto-scroll to bottom on new messages
 *  - Empty / welcome state
 *  - Rendering message list + loading indicator
 */
import { useEffect, useRef } from 'react'
import {
  PlayCircle, MessageSquare, Zap, Lock, ArrowDown,
} from 'lucide-react'
import Message from './Message'
import Loader  from './Loader'

const WELCOME_CARDS = [
  { icon: <PlayCircle size={16} />, title: 'Any YouTube Video', body: 'Paste a URL and start asking. Works with lectures, tutorials, podcasts, and more.' },
  { icon: <MessageSquare size={16} />, title: 'Natural Language', body: 'Ask questions exactly as you would to a friend. No special syntax required.' },
  { icon: <Zap size={16} />, title: 'Powered by Google Gemini', body: 'Ultra-fast inference via Google Gemini for near-instant answers.' },
  { icon: <Lock size={16} />, title: 'Grounded Answers', body: 'Every answer is sourced strictly from the video transcript — no hallucinations.' },
]

const ChatBox = ({ messages, isLoading, videoUrl }) => {
  const bottomRef   = useRef(null)
  const containerRef = useRef(null)

  // Auto-scroll whenever messages change or loading starts/stops
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const isEmpty = messages.length === 0

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto py-4"
      style={{ scrollbarGutter: 'stable' }}
    >
      {/* ── Welcome screen ── */}
      {isEmpty && (
        <div className="flex flex-col items-center justify-center h-full px-4 animate-fade-in">
          <div
            className="flex items-center justify-center w-14 h-14 rounded-2xl mb-5"
            style={{ background: 'var(--accent)', boxShadow: '0 0 32px rgba(99,102,241,0.35)' }}
          >
            <PlayCircle size={28} color="#fff" />
          </div>

          <h2 className="text-xl font-bold mb-1.5 tracking-tight" style={{ color: 'var(--text-primary)' }}>
            Ask anything about a video
          </h2>
          <p className="text-sm text-center max-w-sm mb-8" style={{ color: 'var(--text-secondary)' }}>
            Paste a YouTube URL in the sidebar, then ask your questions here.
            VideoMind reads the transcript and answers with source citations.
          </p>

          {/* Feature grid */}
          <div className="welcome-grid w-full max-w-lg">
            {WELCOME_CARDS.map((card) => (
              <div
                key={card.title}
                className="flex flex-col gap-1.5 px-4 py-3.5 rounded-xl"
                style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}
              >
                <span style={{ color: 'var(--accent-hover)' }}>{card.icon}</span>
                <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>
                  {card.title}
                </span>
                <span className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
                  {card.body}
                </span>
              </div>
            ))}
          </div>

          {!videoUrl && (
            <div className="flex items-center gap-2 mt-8 text-xs animate-fade-in" style={{ color: 'var(--text-muted)' }}>
              <ArrowDown size={13} className="animate-bounce" />
              Start by pasting a YouTube URL in the left sidebar
            </div>
          )}
        </div>
      )}

      {/* ── Message list ── */}
      {!isEmpty && (
        <div className="flex flex-col gap-2">
          {messages.map((msg) => (
            <Message key={msg.id} message={msg} />
          ))}
        </div>
      )}

      {/* ── Typing indicator ── */}
      {isLoading && (
        <div className="mt-2">
          <Loader />
        </div>
      )}

      {/* Scroll anchor */}
      <div ref={bottomRef} className="h-2" />
    </div>
  )
}

export default ChatBox
