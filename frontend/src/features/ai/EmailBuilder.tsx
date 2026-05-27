import { useState } from 'react'
import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { Wand2, FileDown } from 'lucide-react'

interface Props {
  /** Pre-fills the brief — e.g. the template/campaign title. */
  defaultTitle?: string
  /** True when rendered inside the editor (enables "Insert into editor"). */
  inEditor?: boolean
}

/** Strip markdown code fences the model may add despite instructions. */
function cleanMjml(raw: string): string {
  let s = raw.trim()
  s = s.replace(/^```(?:mjml|html|xml)?\s*/i, '').replace(/```$/i, '').trim()
  const start = s.indexOf('<mjml')
  const end = s.lastIndexOf('</mjml>')
  if (start !== -1 && end !== -1) s = s.slice(start, end + '</mjml>'.length)
  return s
}

export default function EmailBuilder({ defaultTitle = '', inEditor = false }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType, error } = useAIStore()
  const [title, setTitle] = useState(defaultTitle)
  const [goal, setGoal] = useState('drive engagement and conversions')
  const [industry, setIndustry] = useState('Technology')
  const [keyPoints, setKeyPoints] = useState('')
  const [inserted, setInserted] = useState(false)

  const isActive = isStreaming && jobType === 'email_build'
  const mjml = jobType === 'email_build' ? cleanMjml(streamBuffer) : ''
  const hasResult = !isActive && mjml.includes('<mjml')

  const handleGenerate = () => {
    setInserted(false)
    startStream({
      jobType: 'email_build',
      inputData: { title: title || 'Email Campaign', goal, industry, key_points: keyPoints },
    })
  }

  const handleInsert = () => {
    window.dispatchEvent(new CustomEvent('editor:load-mjml', { detail: mjml }))
    setInserted(true)
  }

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">
        Describe the email and let AI design the full layout for you.
      </p>

      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title / theme (e.g. Cloud Migration Offer)"
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      />
      <input
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        placeholder="Goal (e.g. book a demo)"
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      />
      <select
        value={industry}
        onChange={(e) => setIndustry(e.target.value)}
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      >
        <option>Technology</option>
        <option>Cloud Computing</option>
        <option>Travel &amp; Logistics</option>
        <option>Analytics</option>
        <option>Enterprise</option>
      </select>
      <textarea
        value={keyPoints}
        onChange={(e) => setKeyPoints(e.target.value)}
        rows={2}
        placeholder="Key points to include (optional)"
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      />

      <button
        onClick={handleGenerate}
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50"
      >
        <Wand2 size={13} />
        {isActive ? 'Designing your email...' : 'Generate Full Email'}
      </button>

      {isActive && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
          Writing MJML...
        </div>
      )}

      {error && jobType === 'email_build' && <p className="text-xs text-destructive">{error}</p>}

      {hasResult && inEditor && (
        <button
          onClick={handleInsert}
          className="w-full flex items-center justify-center gap-2 py-2 bg-accent text-foreground rounded-lg text-xs font-medium border border-border hover:bg-accent/80"
        >
          <FileDown size={13} />
          {inserted ? 'Inserted ✓ — review the canvas' : 'Insert into Editor'}
        </button>
      )}

      {hasResult && !inEditor && (
        <p className="text-xs text-muted-foreground">
          Open this campaign's template in the editor to insert the generated design.
        </p>
      )}

      {(isActive || mjml) && jobType === 'email_build' && (
        <pre className="text-[10px] leading-relaxed text-muted-foreground bg-accent/50 p-3 rounded-lg max-h-48 overflow-auto whitespace-pre-wrap">
          {mjml || streamBuffer}
        </pre>
      )}
    </div>
  )
}
