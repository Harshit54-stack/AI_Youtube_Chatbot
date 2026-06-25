/**
 * Toast.jsx — Animated toast notification stack (top-right corner).
 */
import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, Info, AlertTriangle, X } from 'lucide-react'
import { useApp } from '../../context/AppContext'

const ICONS = {
  success: <CheckCircle  size={16} />,
  error:   <XCircle      size={16} />,
  info:    <Info         size={16} />,
  warning: <AlertTriangle size={16} />,
}

const COLORS = {
  success: { bg: 'rgba(16,185,129,0.1)',  border: 'rgba(16,185,129,0.25)', color: '#34d399' },
  error:   { bg: 'rgba(239,68,68,0.1)',   border: 'rgba(239,68,68,0.25)',  color: '#f87171' },
  info:    { bg: 'rgba(99,102,241,0.1)',  border: 'rgba(99,102,241,0.25)', color: '#818cf8' },
  warning: { bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.25)', color: '#fbbf24' },
}

const ToastItem = ({ toast, onRemove }) => {
  const [leaving, setLeaving] = useState(false)
  const style = COLORS[toast.type] || COLORS.info

  useEffect(() => {
    const timer = setTimeout(() => {
      setLeaving(true)
      setTimeout(() => onRemove(toast.id), 300)
    }, toast.duration ?? 3500)
    return () => clearTimeout(timer)
  }, [toast.id, toast.duration, onRemove])

  return (
    <div
      className={leaving ? 'animate-toast-out' : 'animate-toast-in'}
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        gap: '0.65rem',
        padding: '0.8rem 1rem',
        borderRadius: '12px',
        background: style.bg,
        border: `1px solid ${style.border}`,
        backdropFilter: 'blur(16px)',
        minWidth: '280px',
        maxWidth: '360px',
        boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        pointerEvents: 'all',
      }}
    >
      <span style={{ color: style.color, marginTop: '1px', flexShrink: 0 }}>
        {ICONS[toast.type]}
      </span>
      <p style={{ fontSize: '0.85rem', color: '#f1f5f9', lineHeight: 1.5, flex: 1 }}>
        {toast.message}
      </p>
      <button
        onClick={() => { setLeaving(true); setTimeout(() => onRemove(toast.id), 300) }}
        style={{
          background: 'none', border: 'none', cursor: 'pointer',
          color: '#6b7280', padding: '1px', flexShrink: 0, marginTop: '1px',
        }}
      >
        <X size={13} />
      </button>
    </div>
  )
}

const Toast = () => {
  const { toasts, removeToast } = useApp()

  return (
    <div
      style={{
        position: 'fixed',
        top: '1rem',
        right: '1rem',
        zIndex: 9999,
        display: 'flex',
        flexDirection: 'column',
        gap: '0.5rem',
        pointerEvents: 'none',
      }}
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} onRemove={removeToast} />
      ))}
    </div>
  )
}

export default Toast
