import { useRef, useState } from 'react'
import { Upload, Trash2, Users, CheckCircle, XCircle, Clock } from 'lucide-react'
import {
  useRecipients,
  useAddRecipients,
  useUploadRecipientsCsv,
  useDeleteRecipient,
} from './useRecipients'

interface Props {
  campaignId: string
  editable: boolean
}

const statusIcon = {
  queued: { icon: Clock, color: 'text-muted-foreground' },
  sent: { icon: CheckCircle, color: 'text-green-400' },
  failed: { icon: XCircle, color: 'text-destructive' },
}

// Pull email addresses out of free-form text (comma / space / newline separated)
function parseEmails(text: string): { email: string; name?: string }[] {
  return text
    .split(/[\s,;]+/)
    .map((t) => t.trim())
    .filter((t) => t.includes('@'))
    .map((email) => ({ email }))
}

export default function RecipientsPanel({ campaignId, editable }: Props) {
  const { data: recipients, isLoading } = useRecipients(campaignId)
  const addMutation = useAddRecipients(campaignId)
  const uploadMutation = useUploadRecipientsCsv(campaignId)
  const deleteMutation = useDeleteRecipient(campaignId)
  const [text, setText] = useState('')
  const [message, setMessage] = useState('')
  const fileRef = useRef<HTMLInputElement>(null)

  const handleAdd = async () => {
    const parsed = parseEmails(text)
    if (parsed.length === 0) {
      setMessage('No valid email addresses found.')
      return
    }
    const res = await addMutation.mutateAsync(parsed)
    setMessage(`Added ${res.created} recipient(s). Total: ${res.total}.`)
    setText('')
  }

  const handleCsv = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const res = await uploadMutation.mutateAsync(file)
    setMessage(`Imported ${res.created} of ${res.total} from CSV.`)
    if (fileRef.current) fileRef.current.value = ''
  }

  const count = recipients?.length || 0

  return (
    <div className="bg-card rounded-xl border border-border p-5">
      <div className="flex items-center gap-2 mb-4">
        <Users size={16} className="text-primary" />
        <h3 className="text-sm font-semibold text-foreground">Recipients</h3>
        <span className="text-xs text-muted-foreground">({count})</span>
      </div>

      {editable && (
        <div className="space-y-3 mb-4">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={3}
            className="w-full px-3 py-2 rounded-lg border border-border bg-input text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            placeholder="Paste emails separated by commas, spaces, or new lines&#10;e.g. alice@acme.com, bob@acme.com"
          />
          <div className="flex gap-2">
            <button
              onClick={handleAdd}
              disabled={addMutation.isPending || !text.trim()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
            >
              {addMutation.isPending ? 'Adding...' : 'Add Recipients'}
            </button>
            <button
              onClick={() => fileRef.current?.click()}
              disabled={uploadMutation.isPending}
              className="flex items-center gap-2 px-4 py-2 rounded-lg border border-border text-muted-foreground hover:bg-accent text-sm disabled:opacity-50"
            >
              <Upload size={14} />
              {uploadMutation.isPending ? 'Uploading...' : 'Upload CSV'}
            </button>
            <input
              ref={fileRef}
              type="file"
              accept=".csv"
              onChange={handleCsv}
              className="hidden"
            />
          </div>
          <p className="text-xs text-muted-foreground">
            CSV format: a header row with <code>email,name</code> (extra columns become
            personalization fields like <code>{'{{company}}'}</code>).
          </p>
          {message && <p className="text-xs text-primary">{message}</p>}
        </div>
      )}

      {/* List */}
      {isLoading ? (
        <p className="text-xs text-muted-foreground">Loading recipients...</p>
      ) : count === 0 ? (
        <p className="text-xs text-muted-foreground">
          No recipients yet. {editable && 'Add some above before sending.'}
        </p>
      ) : (
        <div className="border border-border rounded-lg overflow-hidden max-h-72 overflow-y-auto">
          <table className="w-full text-sm">
            <tbody className="divide-y divide-border">
              {recipients!.map((r) => {
                const s = statusIcon[r.status]
                const StatusIcon = s.icon
                return (
                  <tr key={r.id} className="hover:bg-accent/50">
                    <td className="px-3 py-2">
                      <p className="text-foreground">{r.email}</p>
                      {r.name && <p className="text-xs text-muted-foreground">{r.name}</p>}
                      {r.error_message && (
                        <p className="text-xs text-destructive">{r.error_message}</p>
                      )}
                    </td>
                    <td className="px-3 py-2 w-24">
                      <span className={`flex items-center gap-1.5 text-xs ${s.color}`}>
                        <StatusIcon size={12} />
                        {r.status}
                      </span>
                    </td>
                    <td className="px-3 py-2 w-10 text-right">
                      {editable && (
                        <button
                          onClick={() => deleteMutation.mutate(r.id)}
                          className="text-muted-foreground hover:text-destructive transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
