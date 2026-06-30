import { useState, useRef, useEffect, useCallback } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  onStop?: () => void
  isStreaming?: boolean
  disabled?: boolean
  placeholder?: string
  showHint?: boolean
  compact?: boolean
}

export function ChatInput({
  onSend,
  onStop,
  isStreaming = false,
  disabled = false,
  placeholder = 'Message...',
  showHint = true,
  compact = false,
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = 'auto'
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`
    }
  }, [message])

  const handleSend = useCallback(() => {
    const trimmedMessage = message.trim()
    if (trimmedMessage && !disabled && !isStreaming) {
      onSend(trimmedMessage)
      setMessage('')
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto'
      }
    }
  }, [message, disabled, isStreaming, onSend])

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleStop = useCallback(() => {
    onStop?.()
  }, [onStop])

  return (
    <div
      className={`w-full flex justify-center ${compact ? '' : 'py-4'}`}
      style={{
        background: 'var(--token-surface-secondary)',
      }}
    >
      <div
        style={{
          maxWidth: '960px',
          width: '100%',
          marginRight: '22px',
        }}
      >
        {/* Composer Container - CSS Grid Layout */}
        <div
          className="composer-container"
          style={{
            background: 'var(--token-surface-primary)',
            border: '1px solid var(--token-border-light)',
          }}
        >
          {/* Leading: Plus button */}
          <div className="composer-leading">
            <button
              className="flex items-center justify-center rounded-full transition-colors hover:opacity-80"
              style={{
                width: '36px',
                height: '36px',
                color: 'var(--token-text-tertiary)',
              }}
              title="Attach"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          {/* Primary: Input textarea - vertically centered */}
          <div className="composer-primary flex items-center">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={disabled}
              placeholder={placeholder}
              rows={1}
              className="w-full resize-none bg-transparent px-1 text-sm focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
              style={{
                minHeight: '24px',
                maxHeight: '200px',
                color: 'var(--token-text-primary)',
                lineHeight: '24px',
              }}
            />
          </div>

          {/* Trailing: Send/Stop button */}
          <div className="composer-trailing">
            {isStreaming ? (
              <button
                onClick={handleStop}
                className="flex items-center justify-center rounded-full transition-colors"
                style={{
                  width: '36px',
                  height: '36px',
                  background: 'var(--token-text-primary)',
                  color: 'var(--token-surface-primary)',
                }}
                title="Stop generating"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              </button>
            ) : (
              <button
                onClick={handleSend}
                disabled={!message.trim() || disabled}
                className="flex items-center justify-center rounded-full transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                style={{
                  width: '36px',
                  height: '36px',
                  background: message.trim() && !disabled ? 'var(--token-text-primary)' : 'var(--token-surface-tertiary)',
                  color: message.trim() && !disabled ? 'var(--token-surface-primary)' : 'var(--token-text-tertiary)',
                }}
                title="Send message"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
              </button>
            )}
          </div>
        </div>

        {/* Hint */}
        {showHint && (
          <p
            className="text-center text-xs mt-2"
            style={{ color: 'var(--token-text-tertiary)' }}
          >
            <kbd
              className="px-1.5 py-0.5 rounded text-xs font-mono"
              style={{
                background: 'var(--token-surface-tertiary)',
                color: 'var(--token-text-secondary)',
              }}
            >
              Shift + Enter
            </kbd>
            <span className="mx-1"> for new line</span>
          </p>
        )}
      </div>
    </div>
  )
}
