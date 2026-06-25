/**
 * InputBar.jsx — Bottom chat input area.
 */
import { useState, useRef, useEffect } from 'react'
import { Send, AlertCircle } from 'lucide-react'

const MAX_CHARS = 1000

const InputBar = ({ onSend, isLoading, error, videoUrl }) => {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  const canSend = value.trim().length > 0 && !isLoading && !!videoUrl

  // Auto-resize
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 180) + 'px'
  }, [value])

  const handleSend = () => {
    if (!canSend) return
    onSend(value.trim())
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div style={{
      padding: '0.75rem 1rem 1rem',
      background: 'var(--bg-primary)',
      borderTop: '1px solid var(--border)',
      position: 'relative',
      zIndex: 10,
    }}>
      {/* ── Error bar ── */}
      {error && (
        <div className="animate-fade-slide-up" style={{
          display: 'flex', alignItems: 'center', gap: '0.4rem',
          background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)',
          color: 'var(--error)', padding: '0.5rem 0.75rem', borderRadius: '8px',
          fontSize: '0.78rem', marginBottom: '0.75rem',
        }}>
          <AlertCircle size={14} />
          {error}
        </div>
      )}

      {/* ── Input container ── */}
      <div style={{
        display: 'flex', alignItems: 'flex-end', gap: '0.5rem',
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '16px',
        padding: '0.5rem 0.5rem 0.5rem 1rem',
        boxShadow: '0 4px 16px rgba(0,0,0,0.2)',
        transition: 'border-color 0.2s',
      }}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => {
            if (e.target.value.length <= MAX_CHARS) setValue(e.target.value)
          }}
          onKeyDown={handleKeyDown}
          placeholder={
            !videoUrl
              ? 'Paste a YouTube URL first…'
              : isLoading
              ? 'Waiting for response…'
              : 'Ask a question about the video…'
          }
          disabled={isLoading || !videoUrl}
          style={{
            flex: 1, resize: 'none', background: 'transparent',
            color: 'var(--text-primary)', fontSize: '0.9rem', lineHeight: 1.5,
            border: 'none', outline: 'none',
            minHeight: '24px', maxHeight: '180px',
            padding: '0.4rem 0',
          }}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', paddingBottom: '0.1rem' }}>
          {value.length > 0 && (
            <span style={{
              fontSize: '0.65rem', color: value.length > MAX_CHARS * 0.9 ? 'var(--warning)' : 'var(--text-muted)',
              fontFamily: "'JetBrains Mono', monospace",
            }}>
              {value.length}/{MAX_CHARS}
            </span>
          )}
          <button
            onClick={handleSend}
            disabled={!canSend}
            className="btn-primary"
            style={{
              width: 36, height: 36, borderRadius: '12px', padding: 0,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              opacity: canSend ? 1 : 0.4,
            }}
          >
            <Send size={16} />
          </button>
        </div>
      </div>
      
      <p style={{ textAlign: 'center', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.6rem' }}>
        AI can make mistakes. Check important info.
      </p>
    </div>
  )
}

export default InputBar
