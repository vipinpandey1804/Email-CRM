import { useNavigate } from 'react-router-dom'
import { Copy, Edit3, Lock } from 'lucide-react'
import type { EmailTemplate } from '@/types'
import { useDuplicateTemplate } from './useTemplates'

interface Props {
  template: EmailTemplate
}

export default function TemplateCard({ template }: Props) {
  const navigate = useNavigate()
  const duplicateMutation = useDuplicateTemplate()

  return (
    <div className="group bg-card border border-border rounded-xl overflow-hidden hover:border-primary/50 transition-colors">
      {/* Thumbnail */}
      <div className="h-40 bg-accent flex items-center justify-center relative">
        {template.thumbnail_url ? (
          <img
            src={template.thumbnail_url}
            alt={template.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="text-center text-muted-foreground">
            <div className="text-4xl mb-2">📧</div>
            <p className="text-xs">{template.category}</p>
          </div>
        )}
        {template.is_system && (
          <div className="absolute top-2 right-2">
            <span className="flex items-center gap-1 text-xs bg-primary/20 text-primary px-2 py-1 rounded">
              <Lock size={10} /> System
            </span>
          </div>
        )}
        {/* Hover overlay */}
        <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
          <button
            onClick={() => navigate(`/editor/${template.id}`)}
            className="flex items-center gap-1.5 px-3 py-2 bg-primary text-white rounded-lg text-xs font-medium"
          >
            <Edit3 size={12} /> Edit
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation()
              duplicateMutation.mutate(template.id)
            }}
            className="flex items-center gap-1.5 px-3 py-2 bg-white/20 text-white rounded-lg text-xs"
          >
            <Copy size={12} /> Copy
          </button>
        </div>
      </div>
      {/* Info */}
      <div className="p-3">
        <p className="font-medium text-foreground text-sm truncate">{template.name}</p>
        <p className="text-xs text-muted-foreground mt-0.5 capitalize">{template.category}</p>
      </div>
    </div>
  )
}
