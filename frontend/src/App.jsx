import { useState, useEffect } from 'react'
import Landing from './pages/Landing'
import ChatApp from './pages/ChatApp'
import { AppProvider } from './context/AppContext'

function App() {
  const [currentView, setCurrentView] = useState('landing')

  // Simple hash routing
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace('#', '')
      if (hash === 'app' || hash === 'landing') {
        setCurrentView(hash)
      } else {
        window.history.replaceState(null, '', '#landing')
        setCurrentView('landing')
      }
    }
    
    // Initial load
    if (!window.location.hash) {
      window.history.replaceState(null, '', '#landing')
    }
    handleHashChange()

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  const handleNavigate = (view) => {
    window.location.hash = view
  }

  return (
    <AppProvider>
      {currentView === 'landing' ? (
        <Landing onNavigate={handleNavigate} />
      ) : (
        <ChatApp onNavigate={handleNavigate} />
      )}
    </AppProvider>
  )
}

export default App
