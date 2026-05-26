import { useEffect, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { getOrgSlug } from '@/lib/utils'
import type { SMTPConfig } from '@/types'
import { CheckCircle, XCircle } from 'lucide-react'

export default function SMTPSetup() {
  const orgSlug = getOrgSlug()
  const qc = useQueryClient()
  const { data: smtp } = useQuery<SMTPConfig>({
    queryKey: ['smtp', orgSlug],
    queryFn: async () => {
      const { data } = await api.get(`/settings/smtp?org_slug=${orgSlug}`)
      return data
    },
    enabled: !!orgSlug,
    retry: false,
  })

  const [form, setForm] = useState({
    host: '',
    port: 587,
    username: '',
    password: '',
    use_tls: true,
    use_ssl: false,
  })
  const [testEmail, setTestEmail] = useState('')
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)

  // Populate the form once SMTP config loads
  useEffect(() => {
    if (smtp) {
      setForm((f) => ({
        ...f,
        host: smtp.host || '',
        port: smtp.port || 587,
        username: smtp.username || '',
        use_tls: smtp.use_tls ?? true,
        use_ssl: smtp.use_ssl ?? false,
      }))
    }
  }, [smtp])

  const saveMutation = useMutation({
    mutationFn: (payload: typeof form) =>
      api.put(`/settings/smtp?org_slug=${orgSlug}`, payload).then((r) => r.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['smtp'] }),
  })

  const testMutation = useMutation({
    mutationFn: (to_email: string) =>
      api.post(`/settings/smtp/test?org_slug=${orgSlug}`, { to_email }).then((r) => r.data),
    onSuccess: (data) => setTestResult(data),
  })

  return (
    <div className="max-w-lg">
      <h2 className="text-xl font-bold text-foreground mb-1">SMTP Configuration</h2>
      <p className="text-muted-foreground text-sm mb-6">Configure your outgoing mail server</p>

      <form
        onSubmit={(e) => {
          e.preventDefault()
          saveMutation.mutate(form)
        }}
        className="space-y-4 bg-card rounded-xl border border-border p-5"
      >
        <div className="grid grid-cols-3 gap-3">
          <div className="col-span-2">
            <label className="block text-xs font-medium text-muted-foreground mb-1">SMTP Host</label>
            <input
              value={form.host}
              onChange={(e) => setForm((f) => ({ ...f, host: e.target.value }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              placeholder="smtp.gmail.com"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1">Port</label>
            <input
              type="number"
              value={form.port}
              onChange={(e) => setForm((f) => ({ ...f, port: parseInt(e.target.value) || 0 }))}
              className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">Username</label>
          <input
            value={form.username}
            onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1">Password</label>
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Leave blank to keep current"
          />
        </div>

        <div className="flex gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.use_tls}
              onChange={(e) => setForm((f) => ({ ...f, use_tls: e.target.checked }))}
              className="w-4 h-4 accent-primary"
            />
            <span className="text-sm text-foreground">Use TLS</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.use_ssl}
              onChange={(e) => setForm((f) => ({ ...f, use_ssl: e.target.checked }))}
              className="w-4 h-4 accent-primary"
            />
            <span className="text-sm text-foreground">Use SSL</span>
          </label>
        </div>

        <div className="flex gap-2 pt-2">
          <button
            type="submit"
            disabled={saveMutation.isPending}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
          >
            {saveMutation.isPending ? 'Saving...' : 'Save Config'}
          </button>
        </div>
      </form>

      {/* Test connection */}
      {smtp && (
        <div className="mt-4 bg-card rounded-xl border border-border p-5">
          <h3 className="text-sm font-semibold text-foreground mb-3">Test Connection</h3>
          <div className="flex gap-2">
            <input
              type="email"
              value={testEmail}
              onChange={(e) => setTestEmail(e.target.value)}
              placeholder="Send test email to..."
              className="flex-1 px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              onClick={() => testMutation.mutate(testEmail)}
              disabled={!testEmail || testMutation.isPending}
              className="px-4 py-2 bg-accent text-foreground rounded-lg text-sm border border-border disabled:opacity-50"
            >
              Test
            </button>
          </div>
          {testResult && (
            <div
              className={`flex items-center gap-2 mt-3 text-sm ${
                testResult.success ? 'text-green-400' : 'text-destructive'
              }`}
            >
              {testResult.success ? <CheckCircle size={16} /> : <XCircle size={16} />}
              {testResult.message}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
