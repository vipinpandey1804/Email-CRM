import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { EmailTemplate } from '@/types'

export function useTemplates(category?: string) {
  const orgSlug = getOrgSlug()
  return useQuery<EmailTemplate[]>({
    queryKey: ['templates', orgSlug, category],
    queryFn: async () => {
      const params = new URLSearchParams({ org_slug: orgSlug })
      if (category) params.append('category', category)
      const { data } = await api.get(`/templates/?${params}`)
      return data
    },
    enabled: !!orgSlug,
  })
}

export function useTemplate(id: string) {
  const orgSlug = getOrgSlug()
  return useQuery<EmailTemplate>({
    queryKey: ['template', id],
    queryFn: async () => {
      const { data } = await api.get(`/templates/${id}?org_slug=${orgSlug}`)
      return data
    },
    enabled: !!id && !!orgSlug,
  })
}

// GrapesJS emits arrays/objects for components & styles, so JSON fields are
// loosely typed here rather than reusing EmailTemplate's stricter shape.
export interface TemplateSavePayload {
  name?: string
  category?: string
  thumbnail_url?: string
  gjs_components?: unknown
  gjs_styles?: unknown
  mjml_source?: string
  html_output?: string
}

export function useSaveTemplate(id: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: TemplateSavePayload) =>
      api.patch(`/templates/${id}?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['template', id] })
      qc.invalidateQueries({ queryKey: ['templates'] })
    },
  })
}

export function useCreateTemplate() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: { name: string; category: string }) =>
      api.post(`/templates/?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] }),
  })
}

export function useDuplicateTemplate() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) =>
      api.post(`/templates/${id}/duplicate?org_slug=${orgSlug}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['templates'] }),
  })
}
