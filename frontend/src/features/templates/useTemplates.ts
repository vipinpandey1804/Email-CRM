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

export function useSaveTemplate(id: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<EmailTemplate>) =>
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
