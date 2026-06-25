/**
 * Topbar.jsx — Premium top navigation bar.
 */
import { PlayCircle, Wifi, WifiOff, Zap, PanelRight, Menu, X, Sparkles } from 'lucide-react'
import { useApp } from '../../context/AppContext'

const Topbar = ({ backendStatus, onNavigate }) => {
  const { sidebarOpen, setSidebarOpen, panelOpen, setPanelOpen } = useApp()
  const isOnline  = backendStatus === 'ok'
  const isUnknown = backendStatus === 'unknown'

  return (
    <header
      style={{
        height: 'var(--topbar-height)',
        background: 'rgba(11,15,25,0.85)',
        backdropFilter: 'blur(20px)',
        WebkitBackdropFilter: 'blur(20px)',
        borderBottom: '1px solid var(--border)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 1rem',
        position: 'sticky',
        top: 0,
        zIndex: 30,
        flexShrink: 0,
      }}
    >
      {/* ── Left: hamburger + brand ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
        {/* Mobile hamburger */}
        <button
          className="btn-ghost"
          style={{ display: 'none', padding: '0.4rem' }}
          id="topbar-hamburger"
          onClick={() => setSidebarOpen(!sidebarOpen)}
          aria-label="Toggle sidebar"
        >
          {sidebarOpen ? <X size={18} /> : <Menu size={18} />}
        </button>

        {/* Brand */}
        <button
          onClick={() => onNavigate?.('landing')}
          style={{
            display: 'flex', alignItems: 'center', gap: '0.6rem',
            background: 'none', border: 'none', cursor: 'pointer', padding: 0,
          }}
        >
          <div style={{
            width: 32, height: 32, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(99,102,241,0.35)',
          }}>
            <PlayCircle size={17} color="#fff" strokeWidth={2.5} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1, textAlign: 'left' }}>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
              VideoMind
              <span style={{ color: 'var(--accent-hover)' }}> AI</span>
            </span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '1px' }}>
              YouTube RAG Chatbot
            </span>
          </div>
        </button>
      </div>

      {/* ── Right: badges + panel toggle ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        {/* Model badge */}
        <span className="badge badge-indigo" style={{ display: 'none' }} id="model-badge">
          <Sparkles size={10} />
          Google Gemini
        </span>
        <span className="badge badge-indigo">
          <Zap size={10} />
          Google Gemini
        </span>

        {/* API status */}
        <span className={`badge ${isUnknown ? 'badge-gray' : isOnline ? 'badge-green' : 'badge-red'}`}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: isUnknown ? '#6b7280' : isOnline ? '#10b981' : '#ef4444',
            animation: isOnline ? 'glowPulse 2s ease-in-out infinite' : 'none',
          }} />
          {isUnknown ? 'Connecting…' : isOnline ? 'API Online' : 'API Offline'}
        </span>

        {/* Panel toggle (desktop) */}
        <button
          className="btn-ghost"
          style={{
            padding: '0.4rem 0.5rem',
            background: panelOpen ? 'var(--accent-muted)' : 'transparent',
            borderColor: panelOpen ? 'rgba(99,102,241,0.3)' : 'var(--border)',
            color: panelOpen ? 'var(--accent-hover)' : 'var(--text-muted)',
          }}
          onClick={() => setPanelOpen(!panelOpen)}
          title="Toggle sources panel"
          id="panel-toggle"
        >
          <PanelRight size={15} />
        </button>
      </div>

      {/* Mobile responsive — hide panel toggle on small screens */}
      <style>{`
        @media (max-width: 768px) {
          #topbar-hamburger { display: flex !important; }
          #model-badge { display: inline-flex !important; }
          #panel-toggle { display: none !important; }
        }
      `}</style>
    </header>
  )
}

export default Topbar
