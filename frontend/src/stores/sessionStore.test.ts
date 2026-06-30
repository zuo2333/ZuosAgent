import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useSessionStore } from '../stores/sessionStore'
import { Session } from '@/types'

// Helper to create a complete Session object
const createMockSession = (overrides: Partial<Session> = {}): Session => ({
  id: 'test-id',
  title: 'Test Session',
  provider_id: null,
  model: null,
  temperature: null,
  max_tokens: null,
  system_prompt: null,
  enabled_tools: [],
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  ...overrides,
})

// Mock the API client
vi.mock('../api/client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { apiClient } from '../api/client'

describe('sessionStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useSessionStore.setState({
      sessions: [],
      currentSession: null,
      messages: [],
      isLoading: false,
      error: null,
    })
    vi.clearAllMocks()
  })

  describe('fetchSessions', () => {
    it('fetches and sets sessions', async () => {
      const mockSessions = [
        { id: '1', title: 'Session 1', created_at: '', updated_at: '' },
        { id: '2', title: 'Session 2', created_at: '', updated_at: '' },
      ]
      vi.mocked(apiClient.get).mockResolvedValue(mockSessions)

      const { result } = renderHook(() => useSessionStore())

      await act(async () => {
        await result.current.fetchSessions()
      })

      expect(result.current.sessions).toEqual(mockSessions)
      expect(result.current.isLoading).toBe(false)
    })

    it('sets error on fetch failure', async () => {
      vi.mocked(apiClient.get).mockRejectedValue(new Error('Fetch failed'))

      const { result } = renderHook(() => useSessionStore())

      await act(async () => {
        await result.current.fetchSessions()
      })

      expect(result.current.error).toBe('Fetch failed')
      expect(result.current.isLoading).toBe(false)
    })
  })

  describe('createSession', () => {
    it('creates a session and adds to list', async () => {
      const newSession = {
        id: 'new-id',
        title: 'New Session',
        created_at: '',
        updated_at: '',
      }
      vi.mocked(apiClient.post).mockResolvedValue(newSession)

      const { result } = renderHook(() => useSessionStore())

      let created: typeof newSession | undefined
      await act(async () => {
        created = await result.current.createSession({ title: 'New Session' })
      })

      expect(created).toEqual(newSession)
      expect(result.current.sessions[0]).toEqual(newSession)
      expect(result.current.currentSession).toEqual(newSession)
      expect(result.current.messages).toEqual([])
    })

    it('sets error on create failure', async () => {
      vi.mocked(apiClient.post).mockRejectedValue(new Error('Create failed'))

      const { result } = renderHook(() => useSessionStore())

      await act(async () => {
        try {
          await result.current.createSession()
        } catch {
          // Expected error
        }
      })

      expect(result.current.error).toBe('Create failed')
    })
  })

  describe('deleteSession', () => {
    it('deletes session from list', async () => {
      const existingSession = createMockSession({ id: 'delete-me', title: 'To Delete' })
      useSessionStore.setState({
        sessions: [existingSession],
        currentSession: existingSession,
      })
      vi.mocked(apiClient.delete).mockResolvedValue(undefined)

      const { result } = renderHook(() => useSessionStore())

      await act(async () => {
        await result.current.deleteSession('delete-me')
      })

      expect(result.current.sessions).toEqual([])
      expect(result.current.currentSession).toBeNull()
      expect(result.current.messages).toEqual([])
    })
  })

  describe('updateSession', () => {
    it('updates session in list', async () => {
      const existingSession = createMockSession({ id: 'update-me', title: 'Original Title' })
      const updatedSession = {
        ...existingSession,
        title: 'Updated Title',
      }
      useSessionStore.setState({
        sessions: [existingSession],
        currentSession: existingSession,
      })
      vi.mocked(apiClient.patch).mockResolvedValue(updatedSession)

      const { result } = renderHook(() => useSessionStore())

      await act(async () => {
        await result.current.updateSession('update-me', { title: 'Updated Title' })
      })

      expect(result.current.sessions[0].title).toBe('Updated Title')
      expect(result.current.currentSession?.title).toBe('Updated Title')
    })
  })

  describe('setCurrentSession', () => {
    it('sets current session', () => {
      const session = createMockSession({ id: 'current', title: 'Current Session' })
      vi.mocked(apiClient.get).mockResolvedValue([])

      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setCurrentSession(session)
      })

      expect(result.current.currentSession).toEqual(session)
    })

    it('clears messages when setting to null', () => {
      useSessionStore.setState({
        messages: [{ id: '1', content: 'test' }] as any,
      })

      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.setCurrentSession(null)
      })

      expect(result.current.messages).toEqual([])
    })
  })

  describe('addMessage', () => {
    it('adds message to list', () => {
      const { result } = renderHook(() => useSessionStore())
      const message = {
        id: 'msg-1',
        session_id: 'session-1',
        role: 'user' as const,
        content: 'Hello',
        tool_calls: [],
        created_at: '',
      }

      act(() => {
        result.current.addMessage(message)
      })

      expect(result.current.messages).toHaveLength(1)
      expect(result.current.messages[0]).toEqual(message)
    })
  })

  describe('setMessages', () => {
    it('sets messages', () => {
      const { result } = renderHook(() => useSessionStore())
      const messages = [
        { id: '1', content: 'msg1' },
        { id: '2', content: 'msg2' },
      ] as any

      act(() => {
        result.current.setMessages(messages)
      })

      expect(result.current.messages).toEqual(messages)
    })
  })

  describe('clearMessages', () => {
    it('clears messages', () => {
      useSessionStore.setState({
        messages: [{ id: '1', content: 'test' }] as any,
      })

      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.clearMessages()
      })

      expect(result.current.messages).toEqual([])
    })
  })

  describe('clearError', () => {
    it('clears error', () => {
      useSessionStore.setState({ error: 'Some error' })

      const { result } = renderHook(() => useSessionStore())

      act(() => {
        result.current.clearError()
      })

      expect(result.current.error).toBeNull()
    })
  })
})
