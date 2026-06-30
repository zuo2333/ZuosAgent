import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { ChatInput } from './ChatInput'

describe('ChatInput', () => {
  const mockOnSend = vi.fn()
  const mockOnStop = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders input field and send button', () => {
    render(<ChatInput onSend={mockOnSend} />)

    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument()
    expect(screen.getByTitle('Send message (Enter)')).toBeInTheDocument()
  })

  it('calls onSend when send button is clicked', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: 'Hello, world!' } })

    const sendButton = screen.getByTitle('Send message (Enter)')
    fireEvent.click(sendButton)

    expect(mockOnSend).toHaveBeenCalledWith('Hello, world!')
  })

  it('calls onSend when Enter key is pressed', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })

    expect(mockOnSend).toHaveBeenCalledWith('Test message')
  })

  it('does not call onSend when Shift+Enter is pressed', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true })

    expect(mockOnSend).not.toHaveBeenCalled()
  })

  it('clears input after sending', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...') as HTMLTextAreaElement
    fireEvent.change(input, { target: { value: 'Test' } })
    fireEvent.click(screen.getByTitle('Send message (Enter)'))

    expect(input.value).toBe('')
  })

  it('disables send button when input is empty', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const sendButton = screen.getByTitle('Send message (Enter)')
    expect(sendButton).toBeDisabled()
  })

  it('disables send button when disabled prop is true', async () => {
    render(<ChatInput onSend={mockOnSend} disabled />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: 'Test' } })

    const sendButton = screen.getByTitle('Send message (Enter)')
    expect(sendButton).toBeDisabled()
  })

  it('shows stop button when streaming', async () => {
    render(<ChatInput onSend={mockOnSend} onStop={mockOnStop} isStreaming />)

    expect(screen.getByTitle('Stop generating')).toBeInTheDocument()
    expect(screen.queryByTitle('Send message (Enter)')).not.toBeInTheDocument()
  })

  it('calls onStop when stop button is clicked', async () => {
    render(<ChatInput onSend={mockOnSend} onStop={mockOnStop} isStreaming />)

    const stopButton = screen.getByTitle('Stop generating')
    fireEvent.click(stopButton)

    expect(mockOnStop).toHaveBeenCalled()
  })

  it('trims whitespace from message before sending', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: '  trimmed message  ' } })
    fireEvent.click(screen.getByTitle('Send message (Enter)'))

    expect(mockOnSend).toHaveBeenCalledWith('trimmed message')
  })

  it('does not send empty or whitespace-only messages', async () => {
    render(<ChatInput onSend={mockOnSend} />)

    const input = screen.getByPlaceholderText('Type your message...')
    fireEvent.change(input, { target: { value: '   ' } })

    const sendButton = screen.getByTitle('Send message (Enter)')
    expect(sendButton).toBeDisabled()
  })

  it('shows custom placeholder', async () => {
    render(<ChatInput onSend={mockOnSend} placeholder="Ask anything..." />)

    expect(screen.getByPlaceholderText('Ask anything...')).toBeInTheDocument()
  })
})
