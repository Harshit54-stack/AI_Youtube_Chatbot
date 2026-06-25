/**
 * Sidebar.jsx — Full left sidebar with video input, chat history, and settings.
 */
import { useState } from 'react'
import {
  Plus, Trash2, MessageSquare, Settings, Zap,
  ChevronDown, ChevronUp, Clock, BarChart3,
} from 'lucide-react'
import VideoCard from './VideoCard'
import { isValidYouTubeUrl } from '../../hooks/useChat'

const Sidebar = ({ videoUrl, setVideoUrl, onClearChat, messages, onNewChat }) => {
  const [showTips, setShowTips] = useState(false)

  const EXAMPLE_URLS = [
    { label: 'Python in 100 Seconds', url: 'https://www.youtube.com/watch?v=x7X9w_GIm1s' },
    { label: 'How GPT Works',         url: 'https://www.youtube.com/watch?v=wjZofJX0v4M' },
    { label: 'Intro to Transformers', url: 'https://www.youtube.com/watch?v=4Bdc55j80l4' },
  ]

  const msgCount  = messages?.length ?? 0
  const aiMsgs    = messages?.filter(m => m.role === 'assistant' && !m.error) ?? []
  const hasVideo  = isValidYouTubeUrl(videoUrl)

  return (
    <aside style={{
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      overflow: 'hidden',
    }}>
      {/* ── Brand header ── */}
      <div style={{
        padding: '1rem',
        borderBottom: '1px solid var(--border)',
        background: 'linear-gradient(180deg, rgba(99,102,241,0.06) 0%, transparent 100%)',
      }}>
        {/* New Chat button */}
        <button
          onClick={onNewChat}
          className="btn-primary"
          style={{ width: '100%', padding: '0.6rem 1rem', borderRadius: '10px', fontSize: '0.83rem' }}
        >
          <Plus size={15} /> New Chat
        </button>
      </div>

      {/* ── Scrollable body ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>

        {/* Video input */}
        <VideoCard videoUrl={videoUrl} setVideoUrl={setVideoUrl} />

        {/* ── Session stats (if active) ── */}
        {msgCount > 0 && (
          <div
            className="animate-fade-in"
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: '12px',
              padding: '0.75rem',
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '0.5rem',
            }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-hover)' }}>{aiMsgs.length}</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '1px' }}>Answers</div>
            </div>
            <div style={{ textAlign: 'center', borderLeft: '1px solid var(--border)', paddingLeft: '0.5rem' }}>
              <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-hover)' }}>{msgCount}</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '1px' }}>Messages</div>
            </div>
          </div>
        )}

        {/* ── Chat history stub ── */}
        <div>
          <div style={{
            display: 'flex', alignItems: 'center', gap: '0.4rem',
            marginBottom: '0.6rem',
          }}>
            <Clock size={11} color="var(--text-muted)" />
            <span style={{ fontSize: '0.69rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
              Recent
            </span>
          </div>
          {msgCount > 0 ? (
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: '10px',
              padding: '0.6rem 0.75rem',
              display: 'flex',
              alignItems: 'flex-start',
              gap: '0.5rem',
              cursor: 'default',
            }}>
              <MessageSquare size={13} color="var(--accent-hover)" style={{ marginTop: '1px', flexShrink: 0 }} />
              <div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 500, lineHeight: 1.3 }}>
                  Current session
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  {msgCount} message{msgCount !== 1 ? 's' : ''}
                </div>
              </div>
            </div>
          ) : (
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center', padding: '0.75rem 0' }}>
              No history yet
            </p>
          )}
        </div>

        {/* ── Example URLs ── */}
        <div>
          <button
            onClick={() => setShowTips(!showTips)}
            style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              width: '100%', background: 'none', border: 'none', cursor: 'pointer',
              marginBottom: '0.5rem',
            }}
          >
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.69rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
              <Zap size={11} color="var(--text-muted)" /> Quick Examples
            </span>
            {showTips
              ? <ChevronUp size={12} color="var(--text-muted)" />
              : <ChevronDown size={12} color="var(--text-muted)" />
            }
          </button>

          {showTips && (
            <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {EXAMPLE_URLS.map((ex) => (
                <button
                  key={ex.url}
                  onClick={() => setVideoUrl(ex.url)}
                  className="nav-item"
                  style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '0.1rem', padding: '0.5rem 0.6rem' }}
                >
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-primary)', fontWeight: 500 }}>{ex.label}</span>
                  <span style={{ fontSize: '0.67rem', color: 'var(--text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', width: '100%' }}>
                    {ex.url.replace('https://', '')}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* ── Model info ── */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '12px',
          padding: '0.75rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', marginBottom: '0.5rem' }}>
            <BarChart3 size={12} color="var(--accent-hover)" />
            <span style={{ fontSize: '0.69rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em', color: 'var(--text-muted)' }}>
              Model Info
            </span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.3rem' }}>
            {[
              ['Provider', 'Google Gemini'],
              ['LLM', 'Gemini 2.5 Flash'],
              ['Embeddings', 'all-MiniLM-L6-v2'],
              ['Vector DB', 'FAISS'],
            ].map(([k, v]) => (
              <div key={k} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)' }}>{k}</span>
                <span style={{ fontSize: '0.73rem', color: 'var(--text-secondary)', fontWeight: 500 }}>{v}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Bottom: clear chat ── */}
      <div style={{
        padding: '0.75rem 1rem',
        borderTop: '1px solid var(--border)',
        display: 'flex', flexDirection: 'column', gap: '0.5rem',
      }}>
        <button
          onClick={onClearChat}
          disabled={msgCount === 0}
          className="btn-ghost"
          style={{
            width: '100%', justifyContent: 'center', padding: '0.55rem',
            opacity: msgCount === 0 ? 0.35 : 1,
            cursor: msgCount === 0 ? 'not-allowed' : 'pointer',
          }}
        >
          <Trash2 size={13} /> Clear Chat
        </button>
        <p style={{ textAlign: 'center', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
          Powered by LangChain · FAISS · Google Gemini
        </p>
      </div>
    </aside>
  )
}

export default Sidebar
