import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { Pen } from 'lucide-react'

interface Props {
  emailBody: string
}

export default function CopyOptimizer({ emailBody }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType, error } = useAIStore()
  const isActive = isStreaming && jobType === 'copy_optimize'

  return (
    <div className="space-y-3">
      <p className="text-xs text-muted-foreground">
        Paste or edit the email body in the editor, then optimize with AI.
      </p>
      <button
        onClick={() =>
          startStream({
            jobType: 'copy_optimize',
            inputData: { copy: emailBody, tone: 'professional' },
          })
        }
        disabled={isActive || !emailBody}
        className="w-full flex items-center justify-center gap-2 py-2 bg-accent text-foreground rounded-lg text-xs font-medium border border-border disabled:opacity-50"
      >
        <Pen size={13} />
        {isActive ? 'Optimizing...' : 'Optimize Copy'}
      </button>
      {error && jobType === 'copy_optimize' && <p className="text-xs text-destructive">{error}</p>}
      {streamBuffer && jobType === 'copy_optimize' && (
        <div className="text-xs text-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg leading-relaxed">
          {streamBuffer}
        </div>
      )}
    </div>
  )
}
