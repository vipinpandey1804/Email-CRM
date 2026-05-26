import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { Campaign } from '@/types'

export function useCampaigns(status?: string) {
  const orgSlug = getOrgSlug()
  return useQuery<Campaign[]>({
    queryKey: ['campaigns', orgSlug, status],
    queryFn: async () => {
      const params = new URLSearchParams({ org_slug: orgSlug })
      if (status) params.append('status', status)
      const { data } = await api.get(`/campaigns/?${params}`)
      return data
    },
    enabled: !!orgSlug,
  })
}

export function useCampaign(id: string) {
  const orgSlug = getOrgSlug()
  return useQuery<Campaign>({
    queryKey: ['campaign', id],
    queryFn: async () => {
      const { data } = await api.get(`/campaigns/${id}?org_slug=${orgSlug}`)
      return data
    },
  })
}

export function useCreateCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<Campaign> & { template_id?: string }) =>
      api.post(`/campaigns/?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useUpdateCampaign(id: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (payload: Partial<Campaign>) =>
      api.patch(`/campaigns/${id}?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['campaigns'] })
      qc.invalidateQueries({ queryKey: ['campaign', id] })
    },
  })
}

export function useDeleteCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) => api.delete(`/campaigns/${id}?org_slug=${orgSlug}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useSendCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (id: string) =>
      api.post(`/campaigns/${id}/send-now?org_slug=${orgSlug}`).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}

export function useScheduleCampaign() {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: ({ id, scheduled_at }: { id: string; scheduled_at: string }) =>
      api.post(`/campaigns/${id}/schedule?org_slug=${orgSlug}`, { scheduled_at }).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['campaigns'] }),
  })
}
