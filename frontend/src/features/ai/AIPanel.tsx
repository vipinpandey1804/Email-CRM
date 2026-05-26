import { useState } from 'react'
import SubjectSuggestions from './SubjectSuggestions'
import SpamChecker from './SpamChecker'
import CopyOptimizer from './CopyOptimizer'
import CTASuggestions from './CTASuggestions'
import { Sparkles, ShieldCheck, Pen, Target } from 'lucide-react'

interface Props {
  campaignId?: string
  subjectLine?: string
  emailBody?: string
}

type Tab = 'subject' | 'spam' | 'copy' | 'cta'

const tabs: { id: Tab; label: string; icon: typeof Sparkles }[] = [
  { id: 'subject', label: 'Subject', icon: Sparkles },
  { id: 'spam', label: 'Spam', icon: ShieldCheck },
  { id: 'copy', label: 'Copy', icon: Pen },
  { id: 'cta', label: 'CTA', icon: Target },
]

export function AIPanel({ campaignId, subjectLine = '', emailBody = '' }: Props) {
  const [activeTab, setActiveTab] = useState<Tab>('subject')

  return (
    <div className="p-4">
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm font-semibold text-foreground">🤖 AI Assistant</span>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-4 gap-1 mb-4 bg-accent rounded-lg p-1">
        {tabs.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex flex-col items-center py-1.5 rounded-md text-xs transition-colors ${
              activeTab === id ? 'bg-card text-foreground' : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <Icon size={12} className="mb-0.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {activeTab === 'subject' && <SubjectSuggestions campaignId={campaignId} />}
      {activeTab === 'spam' && <SpamChecker subject={subjectLine} body={emailBody} />}
      {activeTab === 'copy' && <CopyOptimizer emailBody={emailBody} />}
      {activeTab === 'cta' && <CTASuggestions campaignId={campaignId} />}
    </div>
  )
}

export default AIPanel
