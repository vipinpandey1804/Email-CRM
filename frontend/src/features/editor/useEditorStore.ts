import { create } from 'zustand'

interface EditorState {
  gjsData: { components: unknown; styles: unknown } | null
  isDirty: boolean
  previewMode: 'desktop' | 'mobile'
  lastSaved: Date | null
  setGjsData: (data: { components: unknown; styles: unknown }) => void
  setPreviewMode: (mode: 'desktop' | 'mobile') => void
  markSaved: () => void
  markDirty: () => void
}

export const useEditorStore = create<EditorState>((set) => ({
  gjsData: null,
  isDirty: false,
  previewMode: 'desktop',
  lastSaved: null,
  setGjsData: (data) => set({ gjsData: data }),
  setPreviewMode: (mode) => set({ previewMode: mode }),
  markSaved: () => set({ isDirty: false, lastSaved: new Date() }),
  markDirty: () => set({ isDirty: true }),
}))
