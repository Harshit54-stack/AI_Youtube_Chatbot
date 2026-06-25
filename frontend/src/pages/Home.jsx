/**
 * Home.jsx — Main page assembling Sidebar + Chat area.
 */
import { useState } from 'react'
import Navbar  from '../components/Navbar'
import Sidebar from '../components/Sidebar'
import ChatBox from '../components/ChatBox'
import Footer  from '../components/Footer'
import { useChat } from '../hooks/useChat'

const Home = () => {
  const {
    messages,
    videoUrl,
    setVideoUrl,
    isLoading,
    error,
    setError,
    backendStatus,
    sendMessage,
    clearChat,
  } = useChat()

  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex flex-col h-full" style={{ background: 'var(--bg-primary)' }}>
      {/* ── Navbar ── */}
      <Navbar
        backendStatus={backendStatus}
        onToggleSidebar={() => setSidebarOpen((p) => !p)}
        sidebarOpen={sidebarOpen}
      />

      {/* ── Body ── */}
      <div className="flex flex-1 overflow-hidden relative">

        {/* ── Mobile sidebar overlay ── */}
        {sidebarOpen && (
          <div
            className="sidebar-overlay md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}

        {/* ── Sidebar ── */}
        <aside
          className={`
            absolute md:relative z-50 md:z-auto
            w-72 md:w-64 lg:w-72
            h-full
            transition-transform duration-300 ease-in-out
            ${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          `}
        >
          <Sidebar
            videoUrl={videoUrl}
            setVideoUrl={(url) => {
              setVideoUrl(url)
              setSidebarOpen(false) // close on mobile after URL set
            }}
            onClearChat={clearChat}
            messageCount={messages.length}
          />
        </aside>

        {/* ── Chat area ── */}
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
          <ChatBox
            messages={messages}
            isLoading={isLoading}
            videoUrl={videoUrl}
          />
          <Footer
            onSend={(q) => {
              setError(null)
              sendMessage(q)
            }}
            isLoading={isLoading}
            error={error}
            videoUrl={videoUrl}
          />
        </div>
      </div>
    </div>
  )
}

export default Home
