import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { SessionList } from './SessionList'
import { Session } from '@/types'

// Mock session data
const mockSessions: Session[] = [
  {
    id: 'session-1',
    title: 'Test Session 1',
    provider_id: null,
    model: null,
    temperature: null,
    max_tokens: null,
    system_prompt: null,
    enabled_tools: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: 'session-2',
    title: 'Test Session 2',
    provider_id: null,
    model: null,
    temperature: null,
    max_tokens: null,
    system_prompt: null,
    enabled_tools: [],
    created_at: new Date(Date.now() - 3600000).toISOString(),
    updated_at: new Date(Date.now() - 3600000).toISOString(),
  },
]

describe('SessionList', () => {
  const mockOnSelectSession = vi.fn()
  const mockOnCreateSession = vi.fn()
  const mockOnDeleteSession = vi.fn()
  const mockOnRenameSession = vi.fn()

  const defaultProps = {
    sessions: mockSessions,
    currentSession: null,
    isLoading: false,
    onSelectSession: mockOnSelectSession,
    onCreateSession: mockOnCreateSession,
    onDeleteSession: mockOnDeleteSession,
    onRenameSession: mockOnRenameSession,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders new chat button', () => {
    render(<SessionList {...defaultProps} />)

    expect(screen.getByText('New Chat')).toBeInTheDocument()
  })

  it('calls onCreateSession when new chat button is clicked', () => {
    render(<SessionList {...defaultProps} />)

    fireEvent.click(screen.getByText('New Chat'))
    expect(mockOnCreateSession).toHaveBeenCalled()
  })

  it('renders session list', () => {
    render(<SessionList {...defaultProps} />)

    expect(screen.getByText('Test Session 1')).toBeInTheDocument()
    expect(screen.getByText('Test Session 2')).toBeInTheDocument()
  })

  it('highlights current session', () => {
    render(
      <SessionList
        {...defaultProps}
        currentSession={mockSessions[0]}
      />
    )

    // The current session should have different styling
    const sessionElement = screen.getByText('Test Session 1').closest('div')
    expect(sessionElement?.className).toContain('bg-gray-100')
  })

  it('calls onSelectSession when session is clicked', () => {
    render(<SessionList {...defaultProps} />)

    fireEvent.click(screen.getByText('Test Session 1'))
    expect(mockOnSelectSession).toHaveBeenCalledWith(mockSessions[0])
  })

  it('shows empty state when no sessions', () => {
    render(<SessionList {...defaultProps} sessions={[]} />)

    expect(screen.getByText('No conversations yet')).toBeInTheDocument()
  })

  it('shows session count', () => {
    render(<SessionList {...defaultProps} />)

    expect(screen.getByText('2 conversations')).toBeInTheDocument()
  })

  it('shows singular conversation count', () => {
    render(<SessionList {...defaultProps} sessions={[mockSessions[0]]} />)

    expect(screen.getByText('1 conversation')).toBeInTheDocument()
  })

  it('disables new chat button when loading', () => {
    render(<SessionList {...defaultProps} isLoading />)

    const newChatButton = screen.getByText('New Chat').closest('button')
    expect(newChatButton).toBeDisabled()
  })

  it('formats relative time correctly', () => {
    render(<SessionList {...defaultProps} />)

    // Session 1 is "Just now"
    expect(screen.getByText('Just now')).toBeInTheDocument()
    // Session 2 is 1 hour ago
    expect(screen.getByText('1 hour ago')).toBeInTheDocument()
  })

  it('shows context menu on right click', async () => {
    render(<SessionList {...defaultProps} />)

    const sessionElement = screen.getByText('Test Session 1').closest('div')
    fireEvent.contextMenu(sessionElement!)

    // Context menu should appear with Rename and Delete options
    await waitFor(() => {
      expect(screen.getByText('Rename')).toBeInTheDocument()
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })
  })

  it('calls onDeleteSession when delete is clicked from context menu', async () => {
    render(<SessionList {...defaultProps} />)

    // Open context menu
    const sessionElement = screen.getByText('Test Session 1').closest('div')
    fireEvent.contextMenu(sessionElement!)

    await waitFor(() => {
      expect(screen.getByText('Delete')).toBeInTheDocument()
    })

    // Click delete
    fireEvent.click(screen.getByText('Delete'))
    expect(mockOnDeleteSession).toHaveBeenCalledWith('session-1')
  })

  it('allows renaming session', async () => {
    render(<SessionList {...defaultProps} />)

    // Open context menu
    const sessionElement = screen.getByText('Test Session 1').closest('div')
    fireEvent.contextMenu(sessionElement!)

    await waitFor(() => {
      expect(screen.getByText('Rename')).toBeInTheDocument()
    })

    // Click rename
    fireEvent.click(screen.getByText('Rename'))

    // Input should appear
    const input = screen.getByDisplayValue('Test Session 1')
    expect(input).toBeInTheDocument()

    // Change value and submit
    fireEvent.change(input, { target: { value: 'Renamed Session' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    expect(mockOnRenameSession).toHaveBeenCalledWith('session-1', 'Renamed Session')
  })

  it('limits rename to 100 characters', async () => {
    render(<SessionList {...defaultProps} />)

    // Open context menu and start rename
    const sessionElement = screen.getByText('Test Session 1').closest('div')
    fireEvent.contextMenu(sessionElement!)

    await waitFor(() => {
      expect(screen.getByText('Rename')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Rename'))

    const input = screen.getByDisplayValue('Test Session 1') as HTMLInputElement
    expect(input.maxLength).toBe(100)
  })

  it('cancels rename on Escape key', async () => {
    render(<SessionList {...defaultProps} />)

    // Open context menu and start rename
    const sessionElement = screen.getByText('Test Session 1').closest('div')
    fireEvent.contextMenu(sessionElement!)

    await waitFor(() => {
      expect(screen.getByText('Rename')).toBeInTheDocument()
    })

    fireEvent.click(screen.getByText('Rename'))

    const input = screen.getByDisplayValue('Test Session 1')
    fireEvent.change(input, { target: { value: 'Changed' } })
    fireEvent.keyDown(input, { key: 'Escape' })

    // Should cancel and revert to original
    expect(screen.getByText('Test Session 1')).toBeInTheDocument()
    expect(mockOnRenameSession).not.toHaveBeenCalled()
  })
})
