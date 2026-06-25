/**
 * VideoCard.jsx — YouTube URL input card with validation, animated states,
 *                 and thumbnail preview.
 */
import { useState } from 'react'
import {
  PlaySquare, CheckCircle2, AlertCircle, Loader2,
  ExternalLink, Video, Link2,
} from 'lucide-react'
import { isValidYouTubeUrl } from '../../hooks/useChat'

const getVideoId = (url) => {
  const m = url?.match(/(?:v=|youtu\.be\/|shorts\/)([A-Za-z0-9_-]{11})/)
  return m ? m[1] : null
}

const VideoCard = ({ videoUrl, setVideoUrl }) => {
  const [inputValue, setInputValue] = useState(videoUrl || '')
  const [touched, setTouched]       = useState(false)
  const [imgLoaded, setImgLoaded]   = useState(false)
  const [imgError, setImgError]     = useState(false)

  const isValid    = isValidYouTubeUrl(inputValue)
  const showError  = touched && inputValue.trim() && !isValid
  const videoId    = getVideoId(videoUrl)

  const handleChange = (e) => {
    const val = e.target.value
    setInputValue(val)
    setTouched(false)
    setImgLoaded(false)
    setImgError(false)
    if (isValidYouTubeUrl(val.trim())) {
      setVideoUrl(val.trim())
    }
  }

  const handleBlur = () => {
    setTouched(true)
    if (isValid) setVideoUrl(inputValue.trim())
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      setTouched(true)
      if (isValid) setVideoUrl(inputValue.trim())
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* ── Label ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
        <PlaySquare size={14} color="#ef4444" />
        <span style={{
          fontSize: '0.72rem', fontWeight: 600,
          textTransform: 'uppercase', letterSpacing: '0.06em',
          color: 'var(--text-muted)',
        }}>
          YouTube Video
        </span>
      </div>

      {/* ── Input ── */}
      <div style={{ position: 'relative' }}>
        <div style={{
          position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)',
          pointerEvents: 'none', zIndex: 1,
        }}>
          <Link2 size={14} color={isValid ? 'var(--success)' : 'var(--text-muted)'} />
        </div>
        <input
          type="url"
          value={inputValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder="Paste YouTube URL…"
          className="input-ring"
          style={{
            width: '100%', borderRadius: '10px',
            padding: '0.6rem 2.2rem 0.6rem 2.2rem',
            fontSize: '0.82rem',
            borderColor: showError
              ? 'var(--error)'
              : isValid
              ? 'rgba(16,185,129,0.4)'
              : 'var(--border)',
          }}
        />
        {inputValue.trim() && (
          <span style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)' }}>
            {isValid
              ? <CheckCircle2 size={14} color="var(--success)" />
              : <AlertCircle  size={14} color="var(--error)" />
            }
          </span>
        )}
      </div>

      {/* ── Inline error ── */}
      {showError && (
        <p style={{ fontSize: '0.75rem', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
          <AlertCircle size={11} /> Not a valid YouTube URL
        </p>
      )}

      {/* ── Thumbnail preview ── */}
      {videoId && (
        <div
          className="animate-fade-in"
          style={{
            borderRadius: '12px', overflow: 'hidden',
            border: '1px solid var(--border)',
            background: 'var(--bg-card)',
          }}
        >
          {/* Thumbnail image */}
          <div style={{ position: 'relative', aspectRatio: '16/9', background: 'var(--bg-elevated)' }}>
            {!imgLoaded && !imgError && (
              <div
                className="skeleton"
                style={{ position: 'absolute', inset: 0 }}
              />
            )}
            <img
              src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
              alt="Video thumbnail"
              onLoad={() => setImgLoaded(true)}
              onError={() => { setImgError(true); setImgLoaded(true) }}
              style={{
                width: '100%', height: '100%', objectFit: 'cover',
                opacity: imgLoaded ? 1 : 0,
                transition: 'opacity 0.3s',
              }}
            />
            {/* Play overlay */}
            {imgLoaded && !imgError && (
              <div style={{
                position: 'absolute', inset: 0,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: 'rgba(0,0,0,0.3)',
                opacity: 0, transition: 'opacity 0.2s',
              }}
              onMouseEnter={e => e.currentTarget.style.opacity = 1}
              onMouseLeave={e => e.currentTarget.style.opacity = 0}
              >
                <div style={{
                  width: 40, height: 40, borderRadius: '50%',
                  background: 'rgba(99,102,241,0.9)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <Video size={18} color="#fff" />
                </div>
              </div>
            )}
          </div>

          {/* Meta bar */}
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '0.55rem 0.75rem',
          }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              <span style={{
                width: 6, height: 6, borderRadius: '50%', background: 'var(--success)',
                animation: 'glowPulse 2s ease-in-out infinite',
              }} />
              Video loaded
            </span>
            <a
              href={videoUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', fontSize: '0.72rem', color: 'var(--accent-hover)', textDecoration: 'none' }}
            >
              Open <ExternalLink size={10} />
            </a>
          </div>
        </div>
      )}
    </div>
  )
}

export default VideoCard
