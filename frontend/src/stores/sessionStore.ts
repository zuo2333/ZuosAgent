import { create } from 'zustand'
import { Session, Message, CreateSessionData } from '@/types'
import { apiClient } from '@/api/client'

interface SessionStore {
  sessions: Session[]
  currentSession: Session | null
  messages: Message[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchSessions: () => Promise<void>
  createSession: (data?: CreateSessionData) => Promise<Session>
  deleteSession: (id: string) => Promise<void>
  updateSession: (id: string, data: Partial<Session>) => Promise<void>
  setCurrentSession: (session: Session | null) => void
  fetchMessages: (sessionId: string) => Promise<void>
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
  clearMessages: () => void
  clearError: () => void
  generateTitle: (sessionId: string) => Promise<string>
}

export const useSessionStore = create<SessionStore>((set, get) => ({
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,
  error: null,

  fetchSessions: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<{ sessions: Session[]; total: number }>('/sessions')
      set({ sessions: response.sessions, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch sessions',
        isLoading: false
      })
    }
  },

  createSession: async (data = {}) => {
    set({ isLoading: true, error: null })
    try {
      const session = await apiClient.post<Session>('/sessions', data)
      set(state => ({
        sessions: [session, ...state.sessions],
        currentSession: session,
        messages: [],
        isLoading: false
      }))
      return session
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create session',
        isLoading: false
      })
      throw error
    }
  },

  deleteSession: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.delete(`/sessions/${id}`)
      set(state => ({
        sessions: state.sessions.filter(s => s.id !== id),
        currentSession: state.currentSession?.id === id ? null : state.currentSession,
        messages: state.currentSession?.id === id ? [] : state.messages,
        isLoading: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete session',
        isLoading: false
      })
      // Refresh session list to sync with backend
      get().fetchSessions()
    }
  },

  updateSession: async (id: string, data: Partial<Session>) => {
    set({ isLoading: true, error: null })
    try {
      const session = await apiClient.patch<Session>(`/sessions/${id}`, data)
      set(state => ({
        sessions: state.sessions.map(s => s.id === id ? session : s),
        currentSession: state.currentSession?.id === id ? session : state.currentSession,
        isLoading: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update session',
        isLoading: false
      })
      // Refresh session list to sync with backend
      get().fetchSessions()
    }
  },

  setCurrentSession: (session: Session | null) => {
    set({ currentSession: session })
    // Fetch messages when switching sessions
    if (session) {
      get().fetchMessages(session.id)
    } else {
      set({ messages: [] })
    }
  },

  fetchMessages: async (sessionId: string) => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<{ messages: Message[]; total: number }>(`/sessions/${sessionId}/messages`)
      // Filter out tool messages - they are internal and should not be displayed
      const displayMessages = response.messages.filter(msg => msg.role !== 'tool')
      set({ messages: displayMessages, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch messages',
        isLoading: false,
        currentSession: null,
        messages: []
      })
      // Refresh session list to sync with backend (session may have been deleted)
      get().fetchSessions()
    }
  },

  setMessages: (messages: Message[]) => {
    set({ messages })
  },

  addMessage: (message: Message) => {
    set(state => ({ messages: [...state.messages, message] }))
  },

  clearMessages: () => {
    set({ messages: [] })
  },

  clearError: () => {
    set({ error: null })
  },

  generateTitle: async (sessionId: string) => {
    try {
      const result = await apiClient.post<{ title: string }>(`/sessions/${sessionId}/generate-title`)
      // Update the session in the store
      set(state => ({
        sessions: state.sessions.map(s =>
          s.id === sessionId ? { ...s, title: result.title } : s
        ),
        currentSession: state.currentSession?.id === sessionId
          ? { ...state.currentSession, title: result.title }
          : state.currentSession
      }))
      return result.title
    } catch (error) {
      console.error('Failed to generate title:', error)
      throw error
    }
  }
}))
