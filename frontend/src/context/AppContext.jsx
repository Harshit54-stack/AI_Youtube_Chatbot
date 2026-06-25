/**
 * AppContext.jsx — Global application state.
 * Provides: toast queue, sidebar visibility, right panel visibility.
 */
import { createContext, useContext, useState, useCallback } from 'react'

const AppContext = createContext(null)

let toastId = 0

export const AppProvider = ({ children }) => {
  const [toasts, setToasts]           = useState([])
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [panelOpen, setPanelOpen]     = useState(true)

  // ── Toast ──────────────────────────────────────────────────────────────
  const addToast = useCallback((message, type = 'info', duration = 3500) => {
    const id = ++toastId
    setToasts((prev) => [...prev, { id, message, type, duration }])
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const toast = {
    success: (msg, dur) => addToast(msg, 'success', dur),
    error:   (msg, dur) => addToast(msg, 'error',   dur),
    info:    (msg, dur) => addToast(msg, 'info',     dur),
    warning: (msg, dur) => addToast(msg, 'warning',  dur),
  }

  return (
    <AppContext.Provider value={{
      toasts, addToast, removeToast, toast,
      sidebarOpen, setSidebarOpen,
      panelOpen, setPanelOpen,
    }}>
      {children}
    </AppContext.Provider>
  )
}

export const useApp = () => {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppProvider')
  return ctx
}
