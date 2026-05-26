import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { Organization } from '@/types'

export default function OrgSettings() {
  const orgSlug = getOrgSlug()
  const qc = useQueryClient()

  const { data: org } = useQuery<Organization>({
    queryKey: ['org', orgSlug],
    queryFn: async () => {
      const { data } = await api.get(`/orgs/${orgSlug}`)
      return data
    },
    enabled: !!orgSlug,
  })

  const [orgName, setOrgName] = useState('')
  const [aiKey, setAiKey] = useState('')

  useEffect(() => {
    if (org) setOrgName(org.name)
  }, [org])

  const updateMutation = useMutation({
    mutationFn: (payload: { name?: string }) =>
      api.patch(`/orgs/${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['org'] }),
  })

  const aiKeyMutation = useMutation({
    mutationFn: (key: string) =>
      api.put(`/settings/ai-key?org_slug=${orgSlug}`, { openai_api_key: key }).then((r) => r.data),
  })

  return (
    <div className="max-w-lg space-y-6">
      <div>
        <h2 className="text-xl font-bold text-foreground mb-1">Organization</h2>
        <p className="text-muted-foreground text-sm">Manage your organization settings</p>
      </div>

      <div className="bg-card rounded-xl border border-border p-5 space-y-4">
        <h3 className="text-sm font-semibold text-foreground">General</h3>
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">
            Organization Name
          </label>
          <input
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          onClick={() => updateMutation.mutate({ name: orgName })}
          disabled={updateMutation.isPending}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {updateMutation.isPending ? 'Saving...' : 'Save'}
        </button>
      </div>

      <div className="bg-card rounded-xl border border-border p-5 space-y-4">
        <h3 className="text-sm font-semibold text-foreground">OpenAI API Key</h3>
        <p className="text-xs text-muted-foreground">
          Required for AI features (subject lines, copy optimization, spam check)
        </p>
        <div>
          <input
            type="password"
            value={aiKey}
            onChange={(e) => setAiKey(e.target.value)}
            placeholder="sk-..."
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
          />
        </div>
        <button
          onClick={() => aiKeyMutation.mutate(aiKey)}
          disabled={!aiKey || aiKeyMutation.isPending}
          className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {aiKeyMutation.isPending ? 'Saving...' : 'Update API Key'}
        </button>
        {aiKeyMutation.isSuccess && <p className="text-xs text-green-400">✓ API key updated</p>}
      </div>
    </div>
  )
}
