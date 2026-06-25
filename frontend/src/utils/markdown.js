/**
 * markdown.js — Lightweight Markdown → HTML renderer (no external deps).
 * Supports: headings, bold, italic, inline code, code blocks, 
 *           unordered/ordered lists, blockquotes, tables, line breaks.
 */

export const renderMarkdown = (text = '') => {
  if (!text || typeof text !== 'string') return ''

  let html = text

  // 1. Escape HTML entities first (prevent XSS from API content)
  html = html
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // 2. Fenced code blocks (```lang\n...\n```)
  html = html.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const langLabel = lang ? `<span class="code-lang">${lang}</span>` : ''
    return `<pre>${langLabel}<code>${code.trim()}</code></pre>`
  })

  // 3. Blockquotes (> text)
  html = html.replace(/^&gt;\s+(.+)/gm, '<blockquote>$1</blockquote>')

  // 4. Headings
  html = html.replace(/^### (.+)/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)/gm,  '<h2>$1</h2>')
  html = html.replace(/^# (.+)/gm,   '<h1>$1</h1>')

  // 5. Tables (simple | col | col | format)
  html = html.replace(/\|(.+)\|\n\|[-| :]+\|\n((?:\|.+\|\n?)*)/g, (_, header, rows) => {
    const ths = header.split('|').filter(Boolean).map(c => `<th>${c.trim()}</th>`).join('')
    const trs = rows.trim().split('\n').map(row => {
      const tds = row.split('|').filter(Boolean).map(c => `<td>${c.trim()}</td>`).join('')
      return `<tr>${tds}</tr>`
    }).join('')
    return `<table><thead><tr>${ths}</tr></thead><tbody>${trs}</tbody></table>`
  })

  // 6. Inline code (`code`)
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>')

  // 7. Bold (**text**)
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>')

  // 8. Italic (*text* or _text_)
  html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
  html = html.replace(/_([^_\n]+)_/g, '<em>$1</em>')

  // 9. Unordered lists (- or * items)
  html = html.replace(/((?:^[ \t]*[-*+][ \t]+.+\n?)+)/gm, (block) => {
    const items = block.trim().split('\n').map(line =>
      `<li>${line.replace(/^[ \t]*[-*+][ \t]+/, '').trim()}</li>`
    ).join('')
    return `<ul>${items}</ul>`
  })

  // 10. Ordered lists (1. items)
  html = html.replace(/((?:^\d+\.[ \t]+.+\n?)+)/gm, (block) => {
    const items = block.trim().split('\n').map(line =>
      `<li>${line.replace(/^\d+\.[ \t]+/, '').trim()}</li>`
    ).join('')
    return `<ol>${items}</ol>`
  })

  // 11. Links [text](url)
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')

  // 12. Paragraphs (double newlines) — but not inside pre/ul/ol/table/blockquote
  html = html.replace(/\n{2,}/g, '</p><p>')
  html = `<p>${html}</p>`

  // 13. Single line breaks
  html = html.replace(/\n/g, '<br />')

  // 14. Clean up empty <p> tags
  html = html.replace(/<p>\s*<\/p>/g, '')
  html = html.replace(/<p>(<(?:pre|ul|ol|table|blockquote|h[1-3])>)/g, '$1')
  html = html.replace(/(<\/(?:pre|ul|ol|table|blockquote|h[1-3])>)<\/p>/g, '$1')

  return html
}
