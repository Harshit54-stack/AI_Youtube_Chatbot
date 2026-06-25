/**
 * Footer.jsx — Question input bar pinned to the bottom of the chat area.
 *
 * Features:
 *  - Auto-resize textarea
 *  - Enter to submit (Shift+Enter for newline)
 *  - Disabled state during loading
 *  - Character count
 *  - Inline error display
 */
import { useState, useRef, useEffect } from 'react'
import { SendHorizonal, AlertCircle } from 'lucide-react'

const MAX_CHARS = 500

const Footer = ({ onSend, isLoading, error, videoUrl }) => {
  const [value, setValue]     = useState('')
  const textareaRef           = useRef(null)

  const canSend = value.trim().length > 0 && !isLoading && !!videoUrl

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = Math.min(ta.scrollHeight, 160) + 'px'
  }, [value])

  const handleSend = () => {
    if (!canSend) return
    onSend(value.trim())
    setValue('')
    // Reset height
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div
      className="px-4 md:px-6 py-3 border-t"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
    >
      {/* ── Error bar ── */}
      {error && (
        <div
          className="flex items-start gap-2 mb-2 px-3 py-2 rounded-lg text-xs animate-fade-in"
          style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', color: 'var(--error)' }}
        >
          <AlertCircle size={13} className="shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      {/* ── Input row ── */}
      <div
        className="flex items-end gap-3 rounded-xl px-3 py-2.5"
        style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)' }}
      >
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
              : 'Ask anything about this video…'
          }
          disabled={isLoading || !videoUrl}
          className="flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none"
          style={{
            color: 'var(--text-primary)',
            minHeight: '24px',
            maxHeight: '160px',
            scrollbarWidth: 'thin',
          }}
        />

        {/* ── Right side: char count + send ── */}
        <div className="flex items-center gap-2 shrink-0 pb-0.5">
          {value.length > 0 && (
            <span
              className="text-[10px] tabular-nums"
              style={{ color: value.length > MAX_CHARS * 0.9 ? 'var(--warning)' : 'var(--text-muted)' }}
            >
              {value.length}/{MAX_CHARS}
            </span>
          )}
          <button
            onClick={handleSend}
            disabled={!canSend}
            className="btn-primary w-8 h-8 rounded-lg shrink-0"
            aria-label="Send message"
          >
            <SendHorizonal size={15} />
          </button>
        </div>
      </div>

      {/* ── Hint ── */}
      <p className="text-center text-[10px] mt-1.5" style={{ color: 'var(--text-muted)' }}>
        Enter to send · Shift+Enter for new line · Answers grounded in transcript
      </p>
    </div>
  )
}

export default Footer
