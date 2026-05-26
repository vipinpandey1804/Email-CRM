import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { ShieldCheck } from 'lucide-react'

interface Props {
  subject: string
  body: string
}

export default function SpamChecker({ subject, body }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType, error } = useAIStore()
  const isActive = isStreaming && jobType === 'spam_check'

  const handleCheck = () => {
    startStream({
      jobType: 'spam_check',
      inputData: { subject, body: body.slice(0, 2000) },
    })
  }

  // Extract spam score if present
  const showBuffer = jobType === 'spam_check' ? streamBuffer : ''
  const scoreMatch = showBuffer.match(/SPAM SCORE:\s*(\d+)/i)
  const score = scoreMatch ? parseInt(scoreMatch[1]) : null

  return (
    <div className="space-y-3">
      <button
        onClick={handleCheck}
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-accent text-foreground rounded-lg text-xs font-medium hover:bg-accent/80 border border-border disabled:opacity-50"
      >
        <ShieldCheck size={13} />
        {isActive ? 'Analyzing...' : 'Check Spam Score'}
      </button>

      {error && jobType === 'spam_check' && <p className="text-xs text-destructive">{error}</p>}

      {score !== null && (
        <div className="flex items-center gap-3 p-3 bg-accent rounded-lg">
          <div
            className="text-2xl font-bold"
            style={{ color: score < 30 ? '#4ade80' : score < 60 ? '#facc15' : '#ef4444' }}
          >
            {score}
          </div>
          <div>
            <p className="text-xs font-medium text-foreground">Spam Score</p>
            <p className="text-xs text-muted-foreground">
              {score < 30 ? 'Low risk' : score < 60 ? 'Medium risk' : 'High risk — action needed'}
            </p>
          </div>
        </div>
      )}

      {showBuffer && (
        <div className="text-xs text-muted-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg font-mono leading-relaxed">
          {showBuffer}
        </div>
      )}
    </div>
  )
}
