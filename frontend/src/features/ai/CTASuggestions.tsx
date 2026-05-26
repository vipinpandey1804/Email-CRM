import { useState } from 'react'
import { useSSEStream } from './useSSEStream'
import { useAIStore } from './useAIStore'
import { Target } from 'lucide-react'

interface Props {
  campaignId?: string
}

export default function CTASuggestions({ campaignId }: Props) {
  const { startStream } = useSSEStream()
  const { isStreaming, streamBuffer, jobType, error } = useAIStore()
  const [goal, setGoal] = useState('schedule a demo')
  const isActive = isStreaming && jobType === 'cta_suggest'

  return (
    <div className="space-y-3">
      <select
        value={goal}
        onChange={(e) => setGoal(e.target.value)}
        className="w-full px-2 py-1.5 rounded-lg border border-border bg-input text-foreground text-xs focus:outline-none"
      >
        <option value="schedule a demo">Schedule a Demo</option>
        <option value="learn more">Learn More</option>
        <option value="contact us">Contact Us</option>
        <option value="start free trial">Start Free Trial</option>
        <option value="book consultation">Book Consultation</option>
      </select>
      <button
        onClick={() =>
          startStream({
            jobType: 'cta_suggest',
            inputData: { campaign_goal: goal, industry: 'Technology' },
            campaignId,
          })
        }
        disabled={isActive}
        className="w-full flex items-center justify-center gap-2 py-2 bg-accent text-foreground rounded-lg text-xs font-medium border border-border disabled:opacity-50"
      >
        <Target size={13} />
        {isActive ? 'Generating...' : 'Generate CTAs'}
      </button>
      {error && jobType === 'cta_suggest' && <p className="text-xs text-destructive">{error}</p>}
      {streamBuffer && jobType === 'cta_suggest' && (
        <div className="text-xs text-foreground whitespace-pre-wrap bg-accent/50 p-3 rounded-lg leading-relaxed">
          {streamBuffer}
        </div>
      )}
    </div>
  )
}
