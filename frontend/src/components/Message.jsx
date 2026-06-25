/**
 * Message.jsx — Single chat bubble for user or AI messages.
 *
 * Features:
 *  - User messages: right-aligned, indigo bubble
 *  - AI messages:   left-aligned, dark card with copy button and sources
 *  - Error state:   red tinted AI bubble
 */
import { useState } from 'react'
import { Copy, Check, AlertTriangle, User } from 'lucide-react'
import SourcesPanel from './SourcesPanel'

const formatTime = (ts) =>
  new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

const Message = ({ message }) => {
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

  // ── User message ──
  if (isUser) {
    return (
      <div className="flex items-start gap-3 justify-end px-4 md:px-6 py-1 animate-fade-slide-up">
        <div className="flex flex-col items-end max-w-[70%]">
          <div
            className="px-4 py-2.5 rounded-2xl rounded-tr-sm text-sm leading-relaxed"
            style={{
              background: 'var(--user-bubble)',
              color: '#fff',
              wordBreak: 'break-word',
            }}
          >
            {message.content}
          </div>
          <span className="text-[10px] mt-1 mr-1" style={{ color: 'var(--text-muted)' }}>
            {formatTime(message.timestamp)}
          </span>
        </div>
        {/* Avatar */}
        <div
          className="flex items-center justify-center w-7 h-7 rounded-full shrink-0 mt-0.5"
          style={{ background: 'rgba(99,102,241,0.2)', border: '1px solid rgba(99,102,241,0.3)' }}
        >
          <User size={13} color="var(--accent-hover)" />
        </div>
      </div>
    )
  }

  // ── AI / Error message ──
  return (
    <div className="flex items-start gap-3 px-4 md:px-6 py-1 animate-fade-slide-up">
      {/* Avatar */}
      <div
        className="flex items-center justify-center w-7 h-7 rounded-full shrink-0 mt-0.5 text-xs font-bold"
        style={{
          background: isError ? 'rgba(239,68,68,0.15)' : 'var(--accent-muted)',
          color: isError ? 'var(--error)' : 'var(--accent-hover)',
          border: `1px solid ${isError ? 'rgba(239,68,68,0.25)' : 'rgba(99,102,241,0.3)'}`,
        }}
      >
        {isError ? <AlertTriangle size={12} /> : 'AI'}
      </div>

      {/* Bubble */}
      <div className="flex flex-col max-w-[75%]" style={{ minWidth: 0 }}>
        <div
          className="px-4 py-3 rounded-2xl rounded-tl-sm relative group"
          style={{
            background: isError ? 'rgba(239,68,68,0.07)' : 'var(--ai-bubble)',
            border: `1px solid ${isError ? 'rgba(239,68,68,0.25)' : 'var(--border)'}`,
            wordBreak: 'break-word',
          }}
        >
          {/* Copy button */}
          {!isError && (
            <button
              onClick={handleCopy}
              className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-md"
              style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)' }}
              title="Copy answer"
            >
              {copied
                ? <Check size={12} color="var(--success)" />
                : <Copy size={12} color="var(--text-muted)" />
              }
            </button>
          )}

          {/* Content */}
          {isError ? (
            <p className="text-sm" style={{ color: 'var(--error)' }}>
              {message.error}
            </p>
          ) : (
            <div className="prose-ai pr-6">
              <div dangerouslySetInnerHTML={{ __html: renderMarkdown(message.content) }} />
              {/* DEBUG */}
              <div style={{ marginTop: '10px', color: 'red', fontSize: '10px' }}>
                RAW CONTENT: {String(message.content)}
                <br />
                RAW DATA FROM API: {JSON.stringify(message.raw_data)}
              </div>
            </div>
          )}

          {/* Sources */}
          {!isError && <SourcesPanel sources={message.sources} />}
        </div>

        <span className="text-[10px] mt-1 ml-1" style={{ color: 'var(--text-muted)' }}>
          VideoMind · {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  )
}

// ── Minimal markdown → HTML renderer ──────────────────────────────────────────
// (no external dependency — handles bold, italic, inline code, code blocks, lists)
const renderMarkdown = (text = '') => {
  if (!text) return ''
  return text
    // Code blocks
    .replace(/```[\w]*\n?([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Unordered lists
    .replace(/^\s*[-*]\s+(.+)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    // Ordered lists
    .replace(/^\d+\.\s+(.+)/gm, '<li>$1</li>')
    // Paragraphs (double newline)
    .replace(/\n{2,}/g, '</p><p>')
    .replace(/^(?!<[uo]l|<pre|<p)(.+)/gm, '<p>$1</p>')
    // Single line breaks
    .replace(/\n/g, '<br />')
}

export default Message
