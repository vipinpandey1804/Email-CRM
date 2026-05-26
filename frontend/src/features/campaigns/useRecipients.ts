import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { CampaignRecipient } from '@/types'

export function useRecipients(campaignId: string) {
  const orgSlug = getOrgSlug()
  return useQuery<CampaignRecipient[]>({
    queryKey: ['recipients', campaignId],
    queryFn: async () => {
      const { data } = await api.get(`/campaigns/${campaignId}/recipients?org_slug=${orgSlug}`)
      return data
    },
    enabled: !!campaignId && !!orgSlug,
  })
}

export function useAddRecipients(campaignId: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (recipients: { email: string; name?: string }[]) =>
      api
        .post(`/campaigns/${campaignId}/recipients/manual?org_slug=${orgSlug}`, { recipients })
        .then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipients', campaignId] }),
  })
}

export function useUploadRecipientsCsv(campaignId: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData()
      form.append('file', file)
      return api
        .post(`/campaigns/${campaignId}/recipients?org_slug=${orgSlug}`, form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        })
        .then((r) => r.data)
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipients', campaignId] }),
  })
}

export function useDeleteRecipient(campaignId: string) {
  const qc = useQueryClient()
  const orgSlug = getOrgSlug()
  return useMutation({
    mutationFn: (recipientId: string) =>
      api.delete(`/campaigns/${campaignId}/recipients/${recipientId}?org_slug=${orgSlug}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['recipients', campaignId] }),
  })
}
