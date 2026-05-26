import { useState } from 'react'
import { Plus } from 'lucide-react'
import { useTemplates, useCreateTemplate } from './useTemplates'
import TemplateCard from './TemplateCard'
import { useNavigate } from 'react-router-dom'

const CATEGORIES = [
  'All',
  'promo',
  'newsletter',
  'announcement',
  'webinar',
  'onboarding',
  'outreach',
]

export default function TemplateLibrary() {
  const [category, setCategory] = useState<string | undefined>()
  const { data: templates, isLoading } = useTemplates(category)
  const createMutation = useCreateTemplate()
  const navigate = useNavigate()

  const handleCreate = async () => {
    const template = await createMutation.mutateAsync({ name: 'New Template', category: 'promo' })
    navigate(`/editor/${template.id}`)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Email Templates</h1>
          <p className="text-muted-foreground text-sm mt-1">{templates?.length || 0} templates</p>
        </div>
        <button
          onClick={handleCreate}
          disabled={createMutation.isPending}
          className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          <Plus size={16} /> New Template
        </button>
      </div>

      {/* Category Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat === 'All' ? undefined : cat)}
            className={`px-3 py-1.5 rounded-lg text-sm capitalize transition-colors ${
              (cat === 'All' && !category) || cat === category
                ? 'bg-primary text-primary-foreground'
                : 'bg-accent text-muted-foreground hover:text-foreground'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full" />
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {templates?.map((t) => (
            <TemplateCard key={t.id} template={t} />
          ))}
        </div>
      )}
    </div>
  )
}
