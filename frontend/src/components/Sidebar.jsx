/**
 * Sidebar.jsx — Video URL input panel + session controls.
 */
import { useState } from 'react'
import {
  Link2, CheckCircle2, AlertCircle, Trash2, Info,
  Video, ExternalLink, ChevronDown, ChevronUp,
} from 'lucide-react'
import { isValidYouTubeUrl } from '../hooks/useChat'

const Sidebar = ({ videoUrl, setVideoUrl, onClearChat, messageCount }) => {
  const [inputValue, setInputValue] = useState(videoUrl)
  const [touched, setTouched]       = useState(false)
  const [showTips, setShowTips]     = useState(false)

  const isValid   = isValidYouTubeUrl(inputValue)
  const showError = touched && inputValue.trim() && !isValid

  const handleApply = () => {
    if (isValid) {
      setVideoUrl(inputValue.trim())
      setTouched(false)
    } else {
      setTouched(true)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') handleApply()
  }

  const handleChange = (e) => {
    setInputValue(e.target.value)
    setTouched(false)
    // Auto-apply when valid
    if (isValidYouTubeUrl(e.target.value.trim())) {
      setVideoUrl(e.target.value.trim())
    }
  }

  // Extract video ID for thumbnail preview
  const getVideoId = (url) => {
    const m = url?.match(/(?:v=|youtu\.be\/|shorts\/)([A-Za-z0-9_-]{11})/)
    return m ? m[1] : null
  }
  const videoId = getVideoId(videoUrl)

  const EXAMPLE_URLS = [
    { label: 'Python in 100 Seconds', url: 'https://www.youtube.com/watch?v=x7X9w_GIm1s' },
    { label: 'How GPT Works', url: 'https://www.youtube.com/watch?v=wjZofJX0v4M' },
  ]

  return (
    <aside
      className="flex flex-col h-full p-4 gap-4 overflow-y-auto"
      style={{ background: 'var(--bg-secondary)', borderRight: '1px solid var(--border)' }}
    >
      {/* ── Section: Video URL ── */}
      <div>
        <label className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>
          <Link2 size={11} />
          YouTube Video
        </label>

        {/* URL input */}
        <div className="relative">
          <input
            type="url"
            value={inputValue}
            onChange={handleChange}
            onBlur={() => setTouched(true)}
            onKeyDown={handleKeyDown}
            placeholder="Paste YouTube URL…"
            className="input-ring w-full rounded-lg px-3 py-2.5 text-sm pr-8"
          />
          {/* Status icon inside input */}
          {inputValue.trim() && (
            <span className="absolute right-2.5 top-1/2 -translate-y-1/2">
              {isValid
                ? <CheckCircle2 size={15} color="var(--success)" />
                : <AlertCircle  size={15} color="var(--error)" />
              }
            </span>
          )}
        </div>

        {/* Inline error */}
        {showError && (
          <p className="text-xs mt-1.5 flex items-center gap-1" style={{ color: 'var(--error)' }}>
            <AlertCircle size={11} /> Invalid YouTube URL
          </p>
        )}

        {/* Thumbnail preview */}
        {videoId && (
          <div className="mt-3 rounded-xl overflow-hidden border animate-fade-in" style={{ borderColor: 'var(--border)' }}>
            <img
              src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
              alt="Video thumbnail"
              className="w-full object-cover"
              style={{ aspectRatio: '16/9' }}
            />
            <div className="px-3 py-2 flex items-center justify-between" style={{ background: 'var(--bg-card)' }}>
              <span className="flex items-center gap-1.5 text-xs" style={{ color: 'var(--text-secondary)' }}>
                <Video size={12} color="var(--error)" />
                Video loaded
              </span>
              <a
                href={videoUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs"
                style={{ color: 'var(--accent-hover)' }}
              >
                Open <ExternalLink size={10} />
              </a>
            </div>
          </div>
        )}
      </div>

      {/* ── Section: Example URLs ── */}
      <div>
        <button
          onClick={() => setShowTips(!showTips)}
          className="flex items-center justify-between w-full text-xs font-semibold uppercase tracking-wider mb-2"
          style={{ color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}
        >
          <span className="flex items-center gap-1.5"><Info size={11} /> Quick Examples</span>
          {showTips ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        </button>

        {showTips && (
          <div className="flex flex-col gap-1.5 animate-fade-in">
            {EXAMPLE_URLS.map((ex) => (
              <button
                key={ex.url}
                onClick={() => {
                  setInputValue(ex.url)
                  setVideoUrl(ex.url)
                  setTouched(false)
                }}
                className="text-left text-xs px-3 py-2 rounded-lg transition-colors"
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                }}
              >
                <span className="block font-medium" style={{ color: 'var(--text-primary)' }}>{ex.label}</span>
                <span className="block truncate mt-0.5" style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{ex.url}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* ── Spacer ── */}
      <div className="flex-1" />

      {/* ── Session controls ── */}
      <div className="border-t pt-4 flex flex-col gap-2" style={{ borderColor: 'var(--border)' }}>
        {messageCount > 0 && (
          <p className="text-xs text-center" style={{ color: 'var(--text-muted)' }}>
            {messageCount} message{messageCount !== 1 ? 's' : ''} in session
          </p>
        )}
        <button
          onClick={onClearChat}
          disabled={messageCount === 0}
          className="btn-ghost w-full justify-center py-2"
          style={messageCount === 0 ? { opacity: 0.35, cursor: 'not-allowed' } : {}}
        >
          <Trash2 size={13} />
          Clear Chat
        </button>
      </div>

      {/* ── Footer note ── */}
      <p className="text-center text-[10px] leading-relaxed" style={{ color: 'var(--text-muted)' }}>
        Powered by LangChain · FAISS · Google Gemini
      </p>
    </aside>
  )
}

export default Sidebar
