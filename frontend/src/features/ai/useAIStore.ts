import { create } from 'zustand'

interface AIState {
  isStreaming: boolean
  streamBuffer: string
  jobType: string | null
  suggestions: string[]
  currentJobId: string | null
  error: string | null
  setStreaming: (v: boolean) => void
  appendToBuffer: (chunk: string) => void
  clearBuffer: () => void
  setJobType: (type: string) => void
  setJobId: (id: string) => void
  setError: (msg: string | null) => void
  addSuggestion: (s: string) => void
  clearSuggestions: () => void
}

export const useAIStore = create<AIState>((set) => ({
  isStreaming: false,
  streamBuffer: '',
  jobType: null,
  suggestions: [],
  currentJobId: null,
  error: null,
  setStreaming: (v) => set({ isStreaming: v }),
  appendToBuffer: (chunk) => set((s) => ({ streamBuffer: s.streamBuffer + chunk })),
  clearBuffer: () => set({ streamBuffer: '', error: null }),
  setJobType: (type) => set({ jobType: type }),
  setJobId: (id) => set({ currentJobId: id }),
  setError: (msg) => set({ error: msg }),
  addSuggestion: (s) => set((state) => ({ suggestions: [...state.suggestions, s] })),
  clearSuggestions: () => set({ suggestions: [] }),
}))
