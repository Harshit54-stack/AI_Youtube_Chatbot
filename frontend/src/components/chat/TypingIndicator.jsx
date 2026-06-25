/**
 * TypingIndicator.jsx — Multi-step animated loading state shown while the AI responds.
 * Cycles through: Retrieving context… → Searching transcript… → Generating answer…
 */
import { useEffect, useState } from 'react'
import { Sparkles } from 'lucide-react'

const STEPS = [
  'Retrieving context…',
  'Searching transcript…',
  'Generating answer…',
]

const TypingIndicator = () => {
  const [stepIdx, setStepIdx] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setStepIdx((prev) => (prev + 1) % STEPS.length)
    }, 1800)
    return () => clearInterval(interval)
  }, [])

  return (
    <div
      className="animate-fade-slide-up"
      style={{
        display: 'flex', alignItems: 'flex-start', gap: '0.75rem',
        padding: '0.5rem 1rem 0.5rem 1.25rem',
      }}
    >
      {/* Avatar */}
      <div style={{
        width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
        background: 'var(--accent-muted)',
        border: '1px solid rgba(99,102,241,0.3)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        marginTop: '2px',
      }}>
        <Sparkles size={13} color="var(--accent-hover)" />
      </div>

      {/* Bubble */}
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '16px', borderTopLeftRadius: '4px',
        padding: '0.75rem 1rem',
        display: 'flex', flexDirection: 'column', gap: '0.5rem',
        minWidth: '200px',
      }}>
        {/* Dots */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>

        {/* Cycling step label */}
        <div
          key={stepIdx}
          className="animate-fade-in"
          style={{ fontSize: '0.75rem', color: 'var(--text-muted)', letterSpacing: '0.01em' }}
        >
          {STEPS[stepIdx]}
        </div>

        {/* Skeleton preview lines */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.25rem' }}>
          <div className="skeleton" style={{ height: '10px', width: '85%' }} />
          <div className="skeleton" style={{ height: '10px', width: '65%' }} />
          <div className="skeleton" style={{ height: '10px', width: '75%' }} />
        </div>
      </div>
    </div>
  )
}

export default TypingIndicator
