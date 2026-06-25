/**
 * Loader.jsx — Animated typing indicator shown while the AI is responding.
 */
const Loader = () => {
  return (
    <div className="flex items-start gap-3 animate-fade-slide-up px-4 md:px-6 py-1">
      {/* Avatar */}
      <div
        className="flex items-center justify-center w-7 h-7 rounded-full shrink-0 text-xs font-bold"
        style={{ background: 'var(--accent-muted)', color: 'var(--accent-hover)', border: '1px solid rgba(99,102,241,0.3)' }}
      >
        AI
      </div>

      {/* Bubble */}
      <div
        className="flex items-center gap-1.5 px-4 py-3 rounded-2xl rounded-tl-sm"
        style={{ background: 'var(--ai-bubble)', border: '1px solid var(--border)' }}
      >
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="ml-2 text-xs" style={{ color: 'var(--text-muted)' }}>
          Analyzing video…
        </span>
      </div>
    </div>
  )
}

export default Loader
