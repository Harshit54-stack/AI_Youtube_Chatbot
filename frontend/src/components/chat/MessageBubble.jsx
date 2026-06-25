/**
 * MessageBubble.jsx — Premium chat bubble for user and AI messages.
 * Uses the markdown renderer and features copy/regenerate actions.
 */
import { useState } from 'react'
import { User, Copy, Check, Sparkles, AlertTriangle, RotateCcw } from 'lucide-react'
import { renderMarkdown } from '../../utils/markdown'

const formatTime = (ts) => {
  if (!ts) return ''
  return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const MessageBubble = ({ message, onRegenerate }) => {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'
  const isError = !isUser && !!message.error

  const handleCopy = async () => {
    const text = message.content || message.error || ''
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {}
  }

  if (isUser) {
    return (
      <div className="animate-fade-slide-up" style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', padding: '0.5rem 1rem 0.5rem 1.25rem', marginBottom: '0.5rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', maxWidth: '75%' }}>
          <div style={{
            background: 'var(--user-bubble)',
            color: '#fff',
            padding: '0.75rem 1.15rem',
            borderRadius: '16px', borderTopRightRadius: '4px',
            fontSize: '0.9rem', lineHeight: 1.6,
            wordBreak: 'break-word',
            boxShadow: '0 4px 12px rgba(99,102,241,0.2)',
          }}>
            {message.content}
          </div>
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.35rem', marginRight: '0.2rem' }}>
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div style={{
          width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
          background: 'rgba(99,102,241,0.15)',
          border: '1px solid rgba(99,102,241,0.3)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginTop: '2px',
        }}>
          <User size={14} color="var(--accent-hover)" />
        </div>
      </div>
    )
  }

  // AI Message
  return (
    <div className="animate-fade-slide-up" style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', padding: '0.5rem 1rem 0.5rem 1.25rem', marginBottom: '0.5rem' }}>
      {/* Avatar */}
      <div style={{
        width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
        background: isError ? 'rgba(239,68,68,0.1)' : 'var(--accent-muted)',
        border: `1px solid ${isError ? 'rgba(239,68,68,0.25)' : 'rgba(99,102,241,0.3)'}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginTop: '2px',
      }}>
        {isError ? <AlertTriangle size={13} color="var(--error)" /> : <Sparkles size={13} color="var(--accent-hover)" />}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '85%', minWidth: 0 }}>
        {/* Bubble */}
        <div className="group" style={{
          position: 'relative',
          background: isError ? 'rgba(239,68,68,0.04)' : 'var(--ai-bubble)',
          border: `1px solid ${isError ? 'rgba(239,68,68,0.2)' : 'var(--border)'}`,
          borderRadius: '16px', borderTopLeftRadius: '4px',
          padding: '0.85rem 1.15rem',
        }}>
          {/* Action buttons (copy, regenerate) */}
          {!isError && (
            <div
              className="opacity-0 group-hover:opacity-100 transition-opacity"
              style={{
                position: 'absolute', top: '-12px', right: '12px',
                display: 'flex', gap: '0.35rem',
                background: 'var(--bg-elevated)', border: '1px solid var(--border)',
                borderRadius: '8px', padding: '0.2rem',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
              }}
            >
              <button
                onClick={handleCopy}
                className="btn-ghost"
                style={{ padding: '0.3rem', border: 'none' }}
                title="Copy answer"
              >
                {copied ? <Check size={13} color="var(--success)" /> : <Copy size={13} />}
              </button>
              {onRegenerate && (
                <button
                  onClick={onRegenerate}
                  className="btn-ghost"
                  style={{ padding: '0.3rem', border: 'none' }}
                  title="Regenerate answer"
                >
                  <RotateCcw size={13} />
                </button>
              )}
            </div>
          )}

          {/* Content */}
          {isError ? (
            <p style={{ fontSize: '0.85rem', color: 'var(--error)', lineHeight: 1.5 }}>
              {message.error}
            </p>
          ) : (
            <div
              className="prose-ai"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }}
            />
          )}
        </div>

        <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.4rem', marginLeft: '0.2rem' }}>
          VideoMind · {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}

export default MessageBubble
