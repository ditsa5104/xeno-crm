import React from 'react'

// Lightweight markdown renderer for copilot chat bubbles. Handles the subset
// the assistant actually produces: headings, bold/italic, inline code, links,
// bullet/numbered lists, and GFM-style pipe tables. Kept dependency-free to
// avoid pulling a full markdown stack into the bundle.

function renderInline(text, keyPrefix) {
  // Order matters: code first so its contents aren't further parsed.
  const tokens = []
  const regex = /(`[^`]+`)|(\*\*[^*]+\*\*)|(\*[^*]+\*)|(\[[^\]]+\]\([^)]+\))/g
  let lastIndex = 0
  let m
  let i = 0
  while ((m = regex.exec(text)) !== null) {
    if (m.index > lastIndex) tokens.push(text.slice(lastIndex, m.index))
    const tok = m[0]
    if (tok.startsWith('`')) {
      tokens.push(
        <code key={`${keyPrefix}-c${i}`} className="px-1 py-0.5 rounded bg-slate-200/70 text-[0.85em] font-mono">
          {tok.slice(1, -1)}
        </code>
      )
    } else if (tok.startsWith('**')) {
      tokens.push(<strong key={`${keyPrefix}-b${i}`}>{tok.slice(2, -2)}</strong>)
    } else if (tok.startsWith('*')) {
      tokens.push(<em key={`${keyPrefix}-i${i}`}>{tok.slice(1, -1)}</em>)
    } else if (tok.startsWith('[')) {
      const lm = /\[([^\]]+)\]\(([^)]+)\)/.exec(tok)
      tokens.push(
        <a key={`${keyPrefix}-a${i}`} href={lm[2]} target="_blank" rel="noreferrer" className="text-indigo-600 underline">
          {lm[1]}
        </a>
      )
    }
    lastIndex = m.index + tok.length
    i += 1
  }
  if (lastIndex < text.length) tokens.push(text.slice(lastIndex))
  return tokens
}

function splitRow(line) {
  return line.replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
}

export default function Markdown({ content = '' }) {
  const lines = content.replace(/\r\n/g, '\n').split('\n')
  const blocks = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // Table: header row, separator row (---), then body rows.
    if (line.includes('|') && i + 1 < lines.length && /^\s*\|?[\s:-]+\|[\s:|-]*$/.test(lines[i + 1])) {
      const header = splitRow(line)
      const rows = []
      i += 2
      while (i < lines.length && lines[i].includes('|')) {
        rows.push(splitRow(lines[i]))
        i += 1
      }
      blocks.push(
        <div key={`tbl${i}`} className="overflow-x-auto my-2">
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr>
                {header.map((h, hi) => (
                  <th key={hi} className="text-left font-semibold border-b border-slate-300 py-1 pr-3">
                    {renderInline(h, `th${i}-${hi}`)}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, ri) => (
                <tr key={ri}>
                  {r.map((cell, ci) => (
                    <td key={ci} className="border-b border-slate-100 py-1 pr-3 align-top">
                      {renderInline(cell, `td${i}-${ri}-${ci}`)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
      continue
    }

    // Headings
    const h = /^(#{1,4})\s+(.*)$/.exec(line)
    if (h) {
      blocks.push(
        <div key={`h${i}`} className="font-semibold mt-2 mb-1">
          {renderInline(h[2], `h${i}`)}
        </div>
      )
      i += 1
      continue
    }

    // Unordered list
    if (/^\s*[-*]\s+/.test(line)) {
      const items = []
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, ''))
        i += 1
      }
      blocks.push(
        <ul key={`ul${i}`} className="list-disc pl-5 my-1 space-y-0.5">
          {items.map((it, ii) => <li key={ii}>{renderInline(it, `ul${i}-${ii}`)}</li>)}
        </ul>
      )
      continue
    }

    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = []
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, ''))
        i += 1
      }
      blocks.push(
        <ol key={`ol${i}`} className="list-decimal pl-5 my-1 space-y-0.5">
          {items.map((it, ii) => <li key={ii}>{renderInline(it, `ol${i}-${ii}`)}</li>)}
        </ol>
      )
      continue
    }

    // Blank line → spacing
    if (line.trim() === '') {
      blocks.push(<div key={`sp${i}`} className="h-2" />)
      i += 1
      continue
    }

    // Paragraph
    blocks.push(<p key={`p${i}`} className="my-0.5">{renderInline(line, `p${i}`)}</p>)
    i += 1
  }

  return <div className="text-sm leading-relaxed">{blocks}</div>
}
