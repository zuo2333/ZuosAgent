import { useState, useCallback } from 'react'
import { Message } from '@/types'
import { MarkdownRenderer } from './MarkdownRenderer'
import { ToolCallCard } from './ToolCallCard'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
  /** If provided, only render this specific tool call */
  singleToolCallIndex?: number
}

export function MessageBubble({ message, isStreaming = false, singleToolCallIndex }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'
  const hasToolCalls = message.tool_calls && message.tool_calls.length > 0

  // If singleToolCallIndex is provided, only render that specific tool call
  const toolCallToRender = singleToolCallIndex !== undefined && hasToolCalls
    ? message.tool_calls![singleToolCallIndex]
    : null

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      console.error('Failed to copy message')
    }
  }, [message.content])

  // User message - ChatGPT style: bubble + avatar, right aligned
  // Single-line bubble height equals avatar height (32px)
  if (isUser) {
    return (
      <div className="flex w-full justify-end animate-fade-in-up">
        <div className="flex items-center gap-2 max-w-[70%]">
          {/* Bubble - padding: 4px top/bottom, 16px left/right */}
          <div
            className="rounded-[22px]"
            style={{
              background: 'var(--token-surface-tertiary)',
              color: 'var(--token-text-primary)',
              lineHeight: '24px',
              padding: '4px 16px',
            }}
          >
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          </div>
          {/* User Avatar */}
          <div
            className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center"
            style={{
              background: 'var(--token-text-primary)',
              color: 'var(--token-surface-primary)',
            }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        </div>
      </div>
    )
  }

  // AI message - with avatar, full width markdown
  // Avatar centered with content only (excluding copy button)
  return (
    <div className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]">
      {/* Main row: avatar + content (centered together) */}
      <div className="flex items-center" style={{ gap: '12px' }}>
        {/* AI Avatar */}
        <div
          className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
          style={{
            background: 'var(--token-surface-tertiary)',
            color: 'var(--token-text-secondary)',
          }}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>

        {/* Content area - single unit per bubble */}
        <div className="flex-1 flex flex-col gap-2 min-w-0">
          {/* Single tool call (if singleToolCallIndex provided) */}
          {toolCallToRender ? (
            <ToolCallCard key={toolCallToRender.id} toolCall={toolCallToRender} />
          ) : (
            <>
              {/* Markdown content */}
              {(message.content || isStreaming) && (
                <div className="w-full">
                  <div className="prose prose-sm max-w-none">
                    <MarkdownRenderer content={message.content} />
                  </div>

                  {/* Streaming cursor */}
                  {isStreaming && (
                    <span
                      className="inline-block w-0.5 h-4 ml-1 rounded-full animate-pulse"
                      style={{ background: 'var(--token-text-primary)' }}
                    />
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Copy button - below the main row, aligned to content */}
      {!isStreaming && (message.content || hasToolCalls) && (
        <button
          onClick={handleCopy}
          className="self-start p-1 opacity-0 group-hover:opacity-100 transition-all duration-200 mt-2 hover:opacity-70"
          style={{
            marginLeft: '44px', // Align with content (avatar width + gap)
          }}
          title="Copy message"
        >
          {copied ? (
            <svg className="w-5 h-5" style={{ color: 'var(--color-success)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-5 h-5" style={{ color: 'var(--token-text-tertiary)' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          )}
        </button>
      )}
    </div>
  )
}
