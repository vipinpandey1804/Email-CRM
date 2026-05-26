import { useState } from 'react'
import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { Sparkles, Copy, Check } from 'lucide-react'

interface Props {
  campaignId?: string
  campaignName?: string
  onSelect?: (subject: string) => void
}

export default function SubjectSuggestions({ campaignId, campaignName, onSelect }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType, error } = useAIStore()
  const [industry, setIndustry] = useState('Technology')
  const [tone, setTone] = useState('professional')
  const [copied, setCopied] = useState<number | null>(null)

  const isActive = isStreaming && jobType === 'subject_lines'

  const handleGenerate = () => {
    startStream({
      jobType: 'subject_lines',
      inputData: { campaign_name: campaignName || 'Campaign', industry, tone },
      campaignId,
    })
  }

  // Parse numbered lines from stream buffer
  const lines =
    jobType === 'subject_lines'
      ? streamBuffer
          .split('\n')
          .filter((l) => /^\d+\./.test(l.trim()))
          .map((l) => l.replace(/^\d+\.\s*/, '').trim())
      : []

  const handleCopy = (line: string, idx: number) => {
    navigator.clipboard.writeText(line)
    setCopied(idx)
    setTimeout(() => setCopied(null), 1500)
  }

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
        >
          <option>Technology</option>
          <option>Travel &amp; Logistics</option>
          <option>Cloud Computing</option>
          <option>Analytics</option>
          <option>Enterprise</option>
        </select>
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
        >
          <option value="professional">Professional</option>
          <option value="urgent">Urgent</option>
          <option value="friendly">Friendly</option>
          <option value="authoritative">Authoritative</option>
        </select>
      </div>

      <button
        onClick={handleGenerate}
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50"
      >
        <Sparkles size={13} />
        {isActive ? 'Generating...' : 'Generate 5 Subject Lines'}
      </button>

      {isActive && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <div className="w-3 h-3 border border-primary border-t-transparent rounded-full animate-spin" />
          AI is writing...
        </div>
      )}

      {error && jobType === 'subject_lines' && (
        <p className="text-xs text-destructive">{error}</p>
      )}

      {lines.length > 0 && (
        <div className="space-y-2">
          {lines.map((line, idx) => (
            <div
              key={idx}
              className="flex items-start justify-between gap-2 p-2 bg-accent rounded-lg group"
            >
              <p className="text-xs text-foreground flex-1">{line}</p>
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleCopy(line, idx)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  {copied === idx ? (
                    <Check size={12} className="text-green-400" />
                  ) : (
                    <Copy size={12} />
                  )}
                </button>
                {onSelect && (
                  <button onClick={() => onSelect(line)} className="text-xs text-primary hover:underline">
                    Use
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {!isActive && jobType === 'subject_lines' && streamBuffer && lines.length === 0 && (
        <p className="text-xs text-muted-foreground whitespace-pre-wrap">{streamBuffer}</p>
      )}
    </div>
  )
}
