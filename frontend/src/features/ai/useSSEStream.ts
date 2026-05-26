import { useCallback } from 'react'
import { useAIStore } from './useAIStore'

/**
 * Maps a logical AI job type to its backend SSE endpoint.
 * These match the async views wired in backend/config/urls.py.
 */
const ENDPOINTS: Record<string, string> = {
  subject_lines: '/ai/subject-lines/stream',
  copy_optimize: '/ai/copy-optimizer/stream',
  spam_check: '/ai/spam-checker/stream',
  cta_suggest: '/ai/cta-optimizer/stream',
}

interface StreamOptions {
  jobType: string
  inputData: Record<string, unknown>
  campaignId?: string
  onComplete?: (fullText: string) => void
}

export function useSSEStream() {
  const { setStreaming, appendToBuffer, clearBuffer, setJobType, setJobId, setError } =
    useAIStore()

  const startStream = useCallback(async (options: StreamOptions) => {
    const token = localStorage.getItem('access_token')
    const endpoint = ENDPOINTS[options.jobType]
    if (!token || !endpoint) return

    setJobType(options.jobType)
    clearBuffer()
    setStreaming(true)

    // Backend derives the org from the authenticated user; input_data is the
    // request body directly. campaign_id is optional metadata.
    const body: Record<string, unknown> = { ...options.inputData }
    if (options.campaignId) body.campaign_id = options.campaignId

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullText = ''
      let buffer = ''

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })

        // SSE events are separated by a blank line; lines start with "data: ".
        const lines = buffer.split('\n')
        // Keep the last (possibly partial) line in the buffer.
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (!trimmed.startsWith('data:')) continue
          const json = trimmed.slice(5).trim()
          if (!json) continue
          try {
            const event = JSON.parse(json)
            if (typeof event.chunk === 'string') {
              appendToBuffer(event.chunk)
              fullText += event.chunk
            } else if (event.done) {
              if (event.job_id) setJobId(event.job_id)
              options.onComplete?.(fullText)
            } else if (event.error) {
              setError(String(event.error))
            }
          } catch {
            /* ignore malformed event fragment */
          }
        }
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Streaming failed')
    } finally {
      setStreaming(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return { startStream }
}
