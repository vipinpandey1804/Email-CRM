import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCreateCampaign } from './useCampaigns'
import { useTemplates } from '@/features/templates/useTemplates'

export default function CreateCampaignWizard() {
  const navigate = useNavigate()
  const createMutation = useCreateCampaign()
  const { data: templates } = useTemplates()
  const [form, setForm] = useState({
    name: '',
    subject_line: '',
    preview_text: '',
    from_name: '',
    from_email: '',
    reply_to: '',
    tags: [] as string[],
    template_id: '',
  })
  const [tagInput, setTagInput] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const payload = {
      ...form,
      template_id: form.template_id || undefined,
    }
    const campaign = await createMutation.mutateAsync(payload)
    if (form.template_id) {
      navigate(`/editor/${form.template_id}?campaign_id=${campaign.id}`)
    } else {
      navigate(`/campaigns/${campaign.id}`)
    }
  }

  const addTag = () => {
    if (tagInput.trim() && !form.tags.includes(tagInput.trim())) {
      setForm((f) => ({ ...f, tags: [...f.tags, tagInput.trim()] }))
      setTagInput('')
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground">New Campaign</h1>
        <p className="text-muted-foreground text-sm mt-1">Set up your email campaign details</p>
      </div>

      <form
        onSubmit={handleSubmit}
        className="space-y-6 bg-card rounded-xl border border-border p-6"
      >
        {/* Campaign Name */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Campaign Name *</label>
          <input
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="e.g. Cloud Transformation Q1 2026"
          />
        </div>

        {/* Subject Line */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Subject Line</label>
          <input
            value={form.subject_line}
            onChange={(e) => setForm((f) => ({ ...f, subject_line: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Transform Your Enterprise Operations"
          />
          <p className="text-xs text-muted-foreground mt-1">
            {form.subject_line.length}/300 characters
          </p>
        </div>

        {/* Preview Text */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Preview Text</label>
          <input
            value={form.preview_text}
            onChange={(e) => setForm((f) => ({ ...f, preview_text: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Discover scalable solutions for your business..."
          />
        </div>

        {/* From */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">From Name</label>
            <input
              value={form.from_name}
              onChange={(e) => setForm((f) => ({ ...f, from_name: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="Maven Technosoft"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">From Email</label>
            <input
              type="email"
              value={form.from_email}
              onChange={(e) => setForm((f) => ({ ...f, from_email: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="noreply@maven.com"
            />
          </div>
        </div>

        {/* Template */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">
            Email Template (optional)
          </label>
          <select
            value={form.template_id}
            onChange={(e) => setForm((f) => ({ ...f, template_id: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="">Start from scratch</option>
            {templates?.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-foreground mb-1">Tags</label>
          <div className="flex gap-2 mb-2">
            <input
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault()
                  addTag()
                }
              }}
              className="flex-1 px-3 py-2 rounded-lg border border-border bg-input text-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
              placeholder="Add tag and press Enter"
            />
            <button
              type="button"
              onClick={addTag}
              className="px-3 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-1">
            {form.tags.map((tag) => (
              <span
                key={tag}
                onClick={() => setForm((f) => ({ ...f, tags: f.tags.filter((t) => t !== tag) }))}
                className="text-xs bg-primary/10 text-primary px-2 py-1 rounded cursor-pointer hover:bg-destructive/10 hover:text-destructive transition-colors"
              >
                {tag} ×
              </span>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3 justify-end pt-2">
          <button
            type="button"
            onClick={() => navigate('/campaigns')}
            className="px-4 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            {createMutation.isPending
              ? 'Creating...'
              : form.template_id
                ? 'Create & Open Editor'
                : 'Create Campaign'}
          </button>
        </div>
      </form>
    </div>
  )
}
