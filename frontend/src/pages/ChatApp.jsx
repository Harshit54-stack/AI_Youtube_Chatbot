/**
 * ChatApp.jsx — The main application shell (sidebar + chat + sources).
 */
import { useEffect } from 'react'
import { useChat } from '../hooks/useChat'
import { useApp } from '../context/AppContext'
import Topbar from '../components/layout/Topbar'
import Sidebar from '../components/sidebar/Sidebar'
import ChatArea from '../components/chat/ChatArea'
import InputBar from '../components/chat/InputBar'
import SourcesPanel from '../components/panels/SourcesPanel'
import Toast from '../components/ui/Toast'

const ChatApp = ({ onNavigate }) => {
  const {
    messages, videoUrl, setVideoUrl, isLoading, error, setError,
    backendStatus, sendMessage, clearChat
  } = useChat()

  const { sidebarOpen, setSidebarOpen, panelOpen } = useApp()

  // Ensure sidebar is closed on desktop mount if window is large, but for now we just use CSS media queries
  // to show/hide the sidebar properly. The mobile sidebar is an overlay.

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100dvh', background: 'var(--bg-primary)' }}>
      <Toast />

      {/* ── Topbar ── */}
      <Topbar backendStatus={backendStatus} onNavigate={onNavigate} />

      {/* ── Main content area ── */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden', position: 'relative' }}>
        
        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div
            className="sidebar-overlay animate-fade-in"
            onClick={() => setSidebarOpen(false)}
            style={{ zIndex: 40 }}
          />
        )}

        {/* ── Left Sidebar ── */}
        <div
          id="app-sidebar"
          style={{
            position: 'absolute', top: 0, bottom: 0, left: 0, zIndex: 50,
            width: 'var(--sidebar-width)',
            transform: sidebarOpen ? 'translateX(0)' : 'translateX(-100%)',
            transition: 'transform 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            background: 'var(--bg-secondary)',
          }}
        >
          <Sidebar
            videoUrl={videoUrl}
            setVideoUrl={(url) => {
              setVideoUrl(url)
              setSidebarOpen(false) // auto-close on mobile
            }}
            onClearChat={clearChat}
            messages={messages}
            onNewChat={() => {
              setVideoUrl('')
              clearChat()
              setSidebarOpen(false)
            }}
          />
        </div>

        {/* ── Center Chat Area ── */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, position: 'relative' }}>
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            videoUrl={videoUrl}
            sendMessage={(q) => { setError(null); sendMessage(q); }}
          />
          <InputBar
            onSend={(q) => { setError(null); sendMessage(q); }}
            isLoading={isLoading}
            error={error}
            videoUrl={videoUrl}
          />
        </div>

        {/* ── Right Sources Panel ── */}
        <SourcesPanel
          sources={messages.length > 0 && messages[messages.length - 1].role === 'assistant' ? messages[messages.length - 1].sources : []}
        />
      </div>

      {/* Responsive layout rules */}
      <style>{`
        @media (min-width: 769px) {
          #app-sidebar {
            position: relative !important;
            transform: translateX(0) !important;
            transition: none !important;
          }
        }
        @media (max-width: 768px) {
          :root {
            --sidebar-width: 280px;
          }
        }
      `}</style>
    </div>
  )
}

export default ChatApp
