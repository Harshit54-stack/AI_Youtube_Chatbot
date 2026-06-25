/**
 * SourcesPanel.jsx — Right panel showing retrieved transcript chunks.
 * Collapsible, with relevance labels and expand/collapse per chunk.
 */
import { useState } from 'react'
import { FileText, ChevronDown, ChevronUp, Quote, X } from 'lucide-react'
import { useApp } from '../../context/AppContext'

const SourceChunk = ({ source, index }) => {
  const [expanded, setExpanded] = useState(false)
  const preview = source.content?.slice(0, 120) + (source.content?.length > 120 ? '…' : '')

  return (
    <div className="source-card animate-fade-slide-up">
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: '0.5rem',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span style={{
            width: 20, height: 20, borderRadius: '6px',
            background: 'var(--accent-muted)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.65rem', fontWeight: 700, color: 'var(--accent-hover)',
            flexShrink: 0,
          }}>
            {index}
          </span>
          <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
            Chunk {source.chunk_index ?? index}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span className="badge badge-indigo" style={{ fontSize: '0.62rem', padding: '0.1rem 0.4rem' }}>
            source
          </span>
          <button
            onClick={() => setExpanded(!expanded)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer', padding: '1px',
              color: 'var(--text-muted)',
            }}
            title={expanded ? 'Collapse' : 'Expand'}
          >
            {expanded ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
          </button>
        </div>
      </div>

      {/* Content */}
      <div style={{ display: 'flex', gap: '0.4rem' }}>
        <Quote size={12} color="var(--accent-muted)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <p style={{ fontSize: '0.77rem', lineHeight: 1.65, color: 'var(--text-secondary)', fontFamily: 'inherit' }}>
          {expanded ? source.content : preview}
        </p>
      </div>
    </div>
  )
}

const EmptyState = () => (
  <div style={{ textAlign: 'center', padding: '2rem 1rem', color: 'var(--text-muted)' }}>
    <FileText size={28} style={{ margin: '0 auto 0.75rem', opacity: 0.3 }} />
    <p style={{ fontSize: '0.8rem', lineHeight: 1.6 }}>
      Sources will appear here after you ask a question
    </p>
  </div>
)

const SourcesPanel = ({ sources }) => {
  const { panelOpen, setPanelOpen } = useApp()

  if (!panelOpen) return null

  return (
    <aside
      className="animate-fade-slide-in"
      style={{
        width: 'var(--panel-width)',
        flexShrink: 0,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        background: 'var(--bg-secondary)',
        borderLeft: '1px solid var(--border)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div style={{
        padding: '0.85rem 1rem',
        borderBottom: '1px solid var(--border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <FileText size={14} color="var(--accent-hover)" />
          <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Sources
          </span>
          {sources?.length > 0 && (
            <span className="badge badge-indigo" style={{ fontSize: '0.62rem' }}>
              {sources.length}
            </span>
          )}
        </div>
        <button
          onClick={() => setPanelOpen(false)}
          className="btn-ghost"
          style={{ padding: '0.25rem', border: 'none', background: 'none' }}
          title="Close panel"
        >
          <X size={14} />
        </button>
      </div>

      {/* Description */}
      <div style={{
        padding: '0.6rem 1rem',
        borderBottom: '1px solid var(--border)',
        background: 'rgba(99,102,241,0.04)',
        flexShrink: 0,
      }}>
        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          Transcript chunks retrieved from the video to ground this answer
        </p>
      </div>

      {/* Sources list */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '0.75rem' }}>
        {!sources || sources.length === 0 ? (
          <EmptyState />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {sources.map((src, i) => (
              <SourceChunk key={i} source={src} index={i + 1} />
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}

export default SourcesPanel
