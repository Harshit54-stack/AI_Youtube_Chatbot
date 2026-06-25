/**
 * SourcesPanel.jsx — Collapsible panel showing retrieved transcript chunks.
 */
import { useState } from 'react'
import { ChevronDown, ChevronUp, BookOpen, FileText } from 'lucide-react'

const SourcesPanel = ({ sources }) => {
  const [expanded, setExpanded] = useState(false)

  if (!sources || sources.length === 0) return null

  return (
    <div className="mt-3">
      {/* Toggle header */}
      <button
        onClick={() => setExpanded((p) => !p)}
        className="flex items-center gap-2 text-xs font-medium transition-colors w-full text-left"
        style={{ color: expanded ? 'var(--accent-hover)' : 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer' }}
      >
        <BookOpen size={12} />
        {sources.length} source{sources.length !== 1 ? 's' : ''} retrieved
        {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {/* Source cards */}
      {expanded && (
        <div className="mt-2 flex flex-col gap-2 animate-fade-in">
          {sources.map((source) => (
            <div key={source.chunk_index} className="source-card">
              <div
                className="flex items-center gap-1.5 mb-1.5 text-[10px] font-semibold uppercase tracking-wider"
                style={{ color: 'var(--accent-hover)' }}
              >
                <FileText size={9} />
                Chunk {source.chunk_index}
              </div>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6, fontSize: '0.78rem' }}>
                {source.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SourcesPanel
