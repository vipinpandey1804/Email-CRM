import { useParams, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { useCampaign, useSendCampaign, useScheduleCampaign } from './useCampaigns'
import { useRecipients } from './useRecipients'
import RecipientsPanel from './RecipientsPanel'
import { AIPanel } from '@/features/ai/AIPanel'
import { Send, Edit3, Clock } from 'lucide-react'

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: campaign, isLoading } = useCampaign(id!)
  const { data: recipients } = useRecipients(id!)
  const sendMutation = useSendCampaign()
  const [showSchedule, setShowSchedule] = useState(false)
  const [scheduledAt, setScheduledAt] = useState('')
  const scheduleMutation = useScheduleCampaign()
  const [showAI, setShowAI] = useState(false)
  const [sendError, setSendError] = useState('')

  const recipientCount = recipients?.length ?? 0
  const isDraft = campaign?.status === 'draft'

  const handleSend = async () => {
    setSendError('')
    try {
      await sendMutation.mutateAsync(id!)
    } catch (err: any) {
      setSendError(err.response?.data?.detail || 'Could not send campaign')
    }
  }

  if (isLoading || !campaign)
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    )

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">{campaign.name}</h1>
          <span
            className={`text-xs px-2 py-1 rounded font-medium mt-1 inline-block ${
              campaign.status === 'draft'
                ? 'bg-secondary text-muted-foreground'
                : campaign.status === 'sent'
                  ? 'bg-green-500/10 text-green-400'
                  : campaign.status === 'failed'
                    ? 'bg-destructive/10 text-destructive'
                    : 'bg-yellow-500/10 text-yellow-400'
            }`}
          >
            {campaign.status.toUpperCase()}
          </span>
        </div>
        {campaign.status === 'draft' && (
          <div className="flex gap-2">
            <button
              onClick={() => setShowAI(!showAI)}
              className="px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              🤖 AI Assist
            </button>
            <button
              onClick={() => campaign.template && navigate(`/editor/${campaign.template}`)}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              <Edit3 size={14} /> Edit Template
            </button>
            <button
              onClick={() => setShowSchedule(true)}
              disabled={recipientCount === 0}
              title={recipientCount === 0 ? 'Add at least one recipient first' : ''}
              className="flex items-center gap-2 px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm disabled:opacity-50"
            >
              <Clock size={14} /> Schedule
            </button>
            <button
              onClick={handleSend}
              disabled={sendMutation.isPending || recipientCount === 0}
              title={recipientCount === 0 ? 'Add at least one recipient first' : ''}
              className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              <Send size={14} />
              {sendMutation.isPending ? 'Queuing...' : 'Send Now'}
            </button>
          </div>
        )}
      </div>

      {/* Details */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {[
          { label: 'Subject Line', value: campaign.subject_line || '—' },
          { label: 'Preview Text', value: campaign.preview_text || '—' },
          {
            label: 'From',
            value: campaign.from_email
              ? `${campaign.from_name} <${campaign.from_email}>`
              : '—',
          },
          { label: 'Reply To', value: campaign.reply_to || '—' },
        ].map(({ label, value }) => (
          <div key={label} className="bg-card rounded-lg border border-border p-4">
            <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">{label}</p>
            <p className="text-sm text-foreground">{value}</p>
          </div>
        ))}
      </div>

      {sendError && (
        <div className="mb-4 p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-destructive text-sm">
          {sendError}
        </div>
      )}

      {isDraft && recipientCount === 0 && (
        <div className="mb-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-sm">
          Add at least one recipient below before you can send or schedule this campaign.
        </div>
      )}

      {/* Recipients */}
      <div className="mb-6">
        <RecipientsPanel campaignId={id!} editable={isDraft} />
      </div>

      {/* AI Panel */}
      {showAI && (
        <div className="bg-card rounded-xl border border-border mb-6">
          <AIPanel campaignId={id!} subjectLine={campaign.subject_line} />
        </div>
      )}

      {/* Schedule Modal */}
      {showSchedule && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-xl border border-border p-6 w-96">
            <h3 className="font-semibold text-foreground mb-4">Schedule Campaign</h3>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground mb-4 focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowSchedule(false)}
                className="px-3 py-2 rounded-lg border border-border text-sm text-muted-foreground"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  await scheduleMutation.mutateAsync({
                    id: id!,
                    scheduled_at: new Date(scheduledAt).toISOString(),
                  })
                  setShowSchedule(false)
                }}
                disabled={!scheduledAt || scheduleMutation.isPending}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm disabled:opacity-50"
              >
                Schedule
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
