import { useEffect, useRef } from 'react'
import grapesjs, { type Editor } from 'grapesjs'
import 'grapesjs/dist/css/grapes.min.css'
import gjsMjml from 'grapesjs-mjml'
import type { EmailTemplate } from '@/types'
import { useEditorStore } from './useEditorStore'

interface SavePayload {
  gjs_components: unknown
  gjs_styles: unknown
  mjml_source: string
  html_output: string
}

interface Props {
  template: EmailTemplate
  onSave: (data: SavePayload) => void
}

export default function GrapesEditor({ template, onSave }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const editorRef = useRef<Editor | null>(null)
  const { setGjsData, markDirty, markSaved } = useEditorStore()

  // Keep latest onSave without re-initialising the editor
  const onSaveRef = useRef(onSave)
  onSaveRef.current = onSave

  useEffect(() => {
    if (!containerRef.current || editorRef.current) return

    const editor = grapesjs.init({
      container: containerRef.current,
      height: '100%',
      width: 'auto',
      fromElement: false,
      plugins: [gjsMjml],
      pluginsOpts: {
        // grapesjs-mjml registers under the 'grapesjs-mjml' key
        'grapesjs-mjml': {},
      },
      storageManager: false,
    })

    editorRef.current = editor

    // Load initial MJML if the template has saved markup, else a starter doc
    const initialMjml = template.mjml_source?.trim()
    editor.setComponents(
      initialMjml ||
        `<mjml><mj-body><mj-section><mj-column><mj-text>Start designing your email…</mj-text></mj-column></mj-section></mj-body></mjml>`
    )

    const handleSave = () => {
      let html = ''
      let mjml = ''
      try {
        // grapesjs-mjml exposes 'mjml-get-code' → { html, mjml }
        const result = editor.runCommand('mjml-get-code') as
          | { html?: string; mjml?: string }
          | undefined
        html = result?.html || ''
        mjml = result?.mjml || ''
      } catch {
        html = editor.getHtml()
      }
      if (!mjml) mjml = editor.getHtml()

      const components = editor.getComponents().toJSON()
      const styles = editor.getStyle().toJSON()

      setGjsData({ components, styles })
      onSaveRef.current({
        gjs_components: components,
        gjs_styles: styles,
        mjml_source: mjml,
        html_output: html,
      })
      markSaved()
    }

    // Mark dirty on any change
    editor.on('update', () => markDirty())

    // External save trigger (Save button in EditorPage)
    const onSaveRequest = () => handleSave()
    window.addEventListener('editor:save-request', onSaveRequest)

    // External "load MJML" trigger (AI email builder)
    const onLoadMjml = (e: Event) => {
      const mjml = (e as CustomEvent<string>).detail
      if (mjml && mjml.includes('<mjml')) {
        editor.setComponents(mjml)
        markDirty()
      }
    }
    window.addEventListener('editor:load-mjml', onLoadMjml)

    // Auto-save every 30 seconds
    const autoSaveInterval = window.setInterval(handleSave, 30_000)

    return () => {
      window.clearInterval(autoSaveInterval)
      window.removeEventListener('editor:save-request', onSaveRequest)
      window.removeEventListener('editor:load-mjml', onLoadMjml)
      editor.destroy()
      editorRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [template.id])

  return <div ref={containerRef} style={{ height: '100%', width: '100%' }} className="gjs-editor-wrap" />
}
