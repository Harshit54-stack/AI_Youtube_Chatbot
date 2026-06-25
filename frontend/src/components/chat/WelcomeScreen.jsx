/**
 * WelcomeScreen.jsx — Beautiful empty state shown when no messages exist.
 */
import { PlayCircle, MessageSquare, Zap, Shield, ArrowRight } from 'lucide-react'
import { isValidYouTubeUrl } from '../../hooks/useChat'

const CARDS = [
  {
    icon: <MessageSquare size={18} />,
    title: 'Natural Questions',
    body: 'Ask anything in plain English — "What is the main topic?", "Summarize key points", "What did they say about X?"',
  },
  {
    icon: <Zap size={18} />,
    title: 'Instant Answers',
    body: 'Ultra-fast inference via Google Gemini. Gemini powers your answers in seconds, not minutes.',
  },
  {
    icon: <Shield size={18} />,
    title: 'No Hallucinations',
    body: 'Every answer is grounded strictly in the video transcript. No guessing, no fabrication.',
  },
  {
    icon: <PlayCircle size={18} />,
    title: 'Any YouTube Video',
    body: 'Lectures, tutorials, podcasts, interviews — paste any public YouTube URL and start asking.',
  },
]

const WelcomeScreen = ({ videoUrl }) => {
  const hasVideo = isValidYouTubeUrl(videoUrl)

  return (
    <div
      className="animate-fade-in"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem 1.5rem',
        textAlign: 'center',
        gap: '0',
      }}
    >
      {/* ── Icon ── */}
      <div
        className="animate-float"
        style={{
          width: 64, height: 64,
          borderRadius: '20px',
          background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 0 0 12px rgba(99,102,241,0.08), 0 0 40px rgba(99,102,241,0.25)',
          marginBottom: '1.5rem',
        }}
      >
        <PlayCircle size={30} color="#fff" />
      </div>

      {/* ── Headline ── */}
      <h2 style={{
        fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.03em',
        color: 'var(--text-primary)', marginBottom: '0.5rem',
      }}>
        Ask anything about a video
      </h2>
      <p style={{
        fontSize: '0.88rem', color: 'var(--text-secondary)',
        maxWidth: '420px', lineHeight: 1.65, marginBottom: '2rem',
      }}>
        {hasVideo
          ? 'Your video is loaded. Type your question below to get instant AI-powered answers from the transcript.'
          : 'Paste a YouTube URL in the sidebar, then ask questions here. VideoMind reads the transcript and answers with source citations.'
        }
      </p>

      {/* ── Feature cards grid ── */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '0.75rem',
        width: '100%',
        maxWidth: '500px',
        marginBottom: hasVideo ? '0' : '1.5rem',
      }}>
        {CARDS.map((card) => (
          <div
            key={card.title}
            className="feature-card"
            style={{ padding: '1rem', borderRadius: '12px', textAlign: 'left' }}
          >
            <span style={{ color: 'var(--accent-hover)', display: 'block', marginBottom: '0.5rem' }}>
              {card.icon}
            </span>
            <span style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.3rem' }}>
              {card.title}
            </span>
            <span style={{ display: 'block', fontSize: '0.75rem', color: 'var(--text-secondary)', lineHeight: 1.55 }}>
              {card.body}
            </span>
          </div>
        ))}
      </div>

      {/* ── CTA hint ── */}
      {!hasVideo && (
        <div
          className="animate-fade-in"
          style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem',
            fontSize: '0.8rem', color: 'var(--text-muted)',
            marginTop: '1rem',
          }}
        >
          <ArrowRight size={14} style={{ transform: 'rotate(180deg)' }} />
          Start by pasting a YouTube URL in the left sidebar
        </div>
      )}

      {/* Mobile responsive grid */}
      <style>{`
        @media (max-width: 480px) {
          .welcome-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  )
}

export default WelcomeScreen
