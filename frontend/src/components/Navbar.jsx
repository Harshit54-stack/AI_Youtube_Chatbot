/**
 * Navbar.jsx — Top navigation bar.
 */
import { PlayCircle, Wifi, WifiOff, Zap } from 'lucide-react'

const Navbar = ({ backendStatus, onToggleSidebar, sidebarOpen }) => {
  const isOnline = backendStatus === 'ok'
  const isUnknown = backendStatus === 'unknown'

  return (
    <header
      className="flex items-center justify-between px-4 md:px-6 h-14 border-b shrink-0"
      style={{ borderColor: 'var(--border)', background: 'var(--bg-secondary)' }}
    >
      {/* ── Brand ── */}
      <div className="flex items-center gap-3">
        {/* Mobile hamburger */}
        <button
          onClick={onToggleSidebar}
          className="md:hidden btn-ghost px-2 py-1.5 mr-1"
          aria-label="Toggle sidebar"
        >
          <span className="flex flex-col gap-[5px]">
            <span className={`block h-0.5 w-5 rounded transition-all ${sidebarOpen ? 'rotate-45 translate-y-[7px]' : ''}`} style={{ background: 'var(--text-secondary)' }} />
            <span className={`block h-0.5 w-5 rounded transition-all ${sidebarOpen ? 'opacity-0' : ''}`} style={{ background: 'var(--text-secondary)' }} />
            <span className={`block h-0.5 w-5 rounded transition-all ${sidebarOpen ? '-rotate-45 -translate-y-[7px]' : ''}`} style={{ background: 'var(--text-secondary)' }} />
          </span>
        </button>

        {/* Logo */}
        <div
          className="flex items-center justify-center w-8 h-8 rounded-lg"
          style={{ background: 'var(--accent)' }}
        >
          <PlayCircle size={16} color="#fff" strokeWidth={2.5} />
        </div>

        <div className="flex flex-col leading-none">
          <span className="text-sm font-bold tracking-tight" style={{ color: 'var(--text-primary)' }}>
            VideoMind
          </span>
          <span className="text-[10px]" style={{ color: 'var(--text-muted)' }}>
            YouTube RAG Chatbot
          </span>
        </div>
      </div>

      {/* ── Right side ── */}
      <div className="flex items-center gap-2">
        {/* Model badge */}
        <span className="badge badge-indigo hidden sm:inline-flex">
          <Zap size={10} />
          Google Gemini
        </span>

        {/* Backend status */}
        <span className={`badge ${isUnknown ? 'badge-gray' : isOnline ? 'badge-green' : 'badge-red'}`}>
          {isOnline ? <Wifi size={10} /> : <WifiOff size={10} />}
          {isUnknown ? 'Connecting…' : isOnline ? 'API Online' : 'API Offline'}
        </span>
      </div>
    </header>
  )
}

export default Navbar
