import { Link, useNavigate } from 'react-router-dom'
import { Plus, Send, Clock, CheckCircle, XCircle, FileText, Mail } from 'lucide-react'
import { useCampaigns, useDeleteCampaign } from './useCampaigns'
import { cn } from '@/lib/utils'
import type { Campaign } from '@/types'

const statusConfig = {
  draft: { label: 'Draft', icon: FileText, color: 'text-muted-foreground' },
  scheduled: { label: 'Scheduled', icon: Clock, color: 'text-yellow-400' },
  sending: { label: 'Sending', icon: Send, color: 'text-blue-400' },
  sent: { label: 'Sent', icon: CheckCircle, color: 'text-green-400' },
  failed: { label: 'Failed', icon: XCircle, color: 'text-destructive' },
}

export default function CampaignList() {
  const { data: campaigns, isLoading } = useCampaigns()
  const deleteMutation = useDeleteCampaign()
  const navigate = useNavigate()

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Campaigns</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {campaigns?.length || 0} total campaigns
          </p>
        </div>
        <Link
          to="/campaigns/new"
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
        >
          <Plus size={16} />
          New Campaign
        </Link>
      </div>

      {/* Table */}
      {!campaigns?.length ? (
        <div className="text-center py-16 text-muted-foreground">
          <Mail size={48} className="mx-auto mb-4 opacity-30" />
          <p className="text-lg font-medium">No campaigns yet</p>
          <p className="text-sm">Create your first campaign to get started</p>
        </div>
      ) : (
        <div className="rounded-xl border border-border overflow-hidden">
          <table className="w-full">
            <thead className="bg-accent">
              <tr>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Campaign
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Status
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Subject
                </th>
                <th className="text-left px-4 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Created
                </th>
                <th className="px-4 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {campaigns.map((campaign: Campaign) => {
                const status = statusConfig[campaign.status]
                const StatusIcon = status.icon
                return (
                  <tr
                    key={campaign.id}
                    className="hover:bg-accent/50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/campaigns/${campaign.id}`)}
                  >
                    <td className="px-4 py-3">
                      <p className="font-medium text-foreground text-sm">{campaign.name}</p>
                      {campaign.tags.length > 0 && (
                        <div className="flex gap-1 mt-1">
                          {campaign.tags.slice(0, 3).map((tag) => (
                            <span
                              key={tag}
                              className="text-xs bg-secondary text-muted-foreground px-1.5 py-0.5 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <div className={cn('flex items-center gap-1.5 text-sm', status.color)}>
                        <StatusIcon size={14} />
                        {status.label}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground max-w-xs truncate">
                      {campaign.subject_line || '—'}
                    </td>
                    <td className="px-4 py-3 text-sm text-muted-foreground">
                      {new Date(campaign.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                      {campaign.status === 'draft' && (
                        <button
                          onClick={() => deleteMutation.mutate(campaign.id)}
                          className="text-xs text-muted-foreground hover:text-destructive transition-colors"
                        >
                          Delete
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
