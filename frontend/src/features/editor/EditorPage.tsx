import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useCallback } from 'react'
import { Monitor, Smartphone, Save, ArrowLeft } from 'lucide-react'
import { useTemplate, useSaveTemplate } from '@/features/templates/useTemplates'
import { useEditorStore } from './useEditorStore'
import GrapesEditor from './GrapesEditor'
import SubjectLineBar from './SubjectLineBar'
import { AIPanel } from '@/features/ai/AIPanel'
import { useUpdateCampaign } from '@/features/campaigns/useCampaigns'

interface SavePayload {
  gjs_components: unknown
  gjs_styles: unknown
  mjml_source: string
  html_output: string
}

export default function EditorPage() {
  const { templateId } = useParams<{ templateId: string }>()
  const [searchParams] = useSearchParams()
  const campaignId = searchParams.get('campaign_id') || undefined
  const navigate = useNavigate()
  const { data: template, isLoading } = useTemplate(templateId!)
  const saveMutation = useSaveTemplate(templateId!)
  const updateCampaign = useUpdateCampaign(campaignId || '')
  const { previewMode, setPreviewMode, isDirty, lastSaved } = useEditorStore()
  const [subjectLine, setSubjectLine] = useState('')
  const [showAI, setShowAI] = useState(false)

  const handleSave = useCallback(
    async (data: SavePayload) => {
      const saved = await saveMutation.mutateAsync(data)
      if (campaignId && subjectLine) {
        await updateCampaign.mutateAsync({ subject_line: subjectLine })
      }
      // If the backend forked a system template into our org, the id changed —
      // switch the editor to the new copy so further saves target it.
      if (saved && saved.id && saved.id !== templateId) {
        const qs = campaignId ? `?campaign_id=${campaignId}` : ''
        navigate(`/editor/${saved.id}${qs}`, { replace: true })
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [campaignId, subjectLine, templateId]
  )

  if (isLoading || !template) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Editor TopBar */}
      <div className="flex items-center justify-between px-4 py-2 bg-card border-b border-border h-12 flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors text-sm"
          >
            <ArrowLeft size={16} />
            Back
          </button>
          <span className="text-muted-foreground">/</span>
          <span className="text-sm font-medium text-foreground">{template.name}</span>
          {saveMutation.isError && (
            <span className="text-xs text-destructive">
              ● Save failed
              {(() => {
                const detail = (saveMutation.error as any)?.response?.data?.detail
                return detail ? ` — ${detail}` : ''
              })()}
            </span>
          )}
          {!saveMutation.isError && isDirty && (
            <span className="text-xs text-yellow-400">● Unsaved</span>
          )}
          {!saveMutation.isError && !isDirty && lastSaved && (
            <span className="text-xs text-muted-foreground">
              Saved {lastSaved.toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {/* Preview toggle */}
          <div className="flex items-center bg-accent rounded-lg p-0.5">
            <button
              onClick={() => setPreviewMode('desktop')}
              className={`p-1.5 rounded-md transition-colors ${
                previewMode === 'desktop' ? 'bg-card text-foreground' : 'text-muted-foreground'
              }`}
            >
              <Monitor size={15} />
            </button>
            <button
              onClick={() => setPreviewMode('mobile')}
              className={`p-1.5 rounded-md transition-colors ${
                previewMode === 'mobile' ? 'bg-card text-foreground' : 'text-muted-foreground'
              }`}
            >
              <Smartphone size={15} />
            </button>
          </div>
          <button
            onClick={() => setShowAI(!showAI)}
            className="px-3 py-1.5 rounded-lg border border-border text-muted-foreground hover:bg-accent text-xs"
          >
            🤖 AI
          </button>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent('editor:save-request'))}
            disabled={saveMutation.isPending}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-xs font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            <Save size={13} />
            {saveMutation.isPending ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {/* Subject line bar (only when campaign context) */}
      {campaignId && (
        <SubjectLineBar subjectLine={subjectLine} onSubjectChange={setSubjectLine} />
      )}

      {/* Main editor area */}
      <div className="flex flex-1 overflow-hidden relative">
        <div className={`flex-1 transition-all ${showAI ? 'mr-80' : ''}`}>
          <GrapesEditor template={template} onSave={handleSave} />
        </div>

        {/* AI Sidebar */}
        {showAI && (
          <div className="w-80 border-l border-border bg-card overflow-y-auto flex-shrink-0 absolute right-0 top-0 bottom-0">
            <AIPanel
              campaignId={campaignId}
              subjectLine={subjectLine}
              emailTitle={template.name}
              inEditor
            />
          </div>
        )}
      </div>
    </div>
  )
}
