import { useEffect, useRef } from 'react'
import { Message } from '@/types'
import { MessageBubble } from './MessageBubble'
import { StreamingToolCalls } from './StreamingToolCalls'
import { MarkdownRenderer } from './MarkdownRenderer'

// Streaming tool call type (matches StreamingToolCalls component)
interface StreamingToolCall {
  id: string
  tool_name: string
  arguments: Record<string, unknown>
  status: 'pending' | 'running' | 'success' | 'error' | 'timeout'
  result: string | null
  error: string | null
  startTime: Date | null
  endTime: Date | null
}

interface MessageListProps {
  messages: Message[]
  streamingContent?: string
  isStreaming?: boolean
  streamingToolCalls?: StreamingToolCall[]
}

export function MessageList({ messages, streamingContent, isStreaming = false, streamingToolCalls = [] }: MessageListProps) {
  const listRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent, streamingToolCalls])

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <h2
            className="text-2xl font-semibold mb-2"
            style={{ color: 'var(--token-text-primary)' }}
          >
            今天有什么可以帮您？
          </h2>
          <p
            className="text-sm"
            style={{ color: 'var(--token-text-tertiary)' }}
          >
            发送消息开始对话
          </p>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={listRef}
      className="flex-1 overflow-y-auto w-full flex justify-center"
    >
      {/* Conversation container - fixed max-width, centered, shrinks only when space runs out */}
      <div
        className="flex flex-col"
        style={{
          maxWidth: '960px',
          width: '100%',
          marginRight: '22px',
          paddingTop: '32px',
          paddingBottom: '48px',
          gap: '0',
        }}
      >
        {messages.map((message, index) => {
          const prevMessage = index > 0 ? messages[index - 1] : null

          // For assistant messages with tool_calls, render each tool call as a separate bubble
          // This matches the streaming behavior where each tool call gets its own avatar
          if (message.role === 'assistant' && message.tool_calls && message.tool_calls.length > 0) {
            // Render each tool call as a separate bubble
            const toolCallBubbles = message.tool_calls.map((_, tcIndex) => {
              // Calculate margin for each tool call bubble
              let marginTop = '16px'
              if (tcIndex === 0 && prevMessage) {
                if (prevMessage.role === 'assistant') {
                  marginTop = '2px'
                }
              } else if (tcIndex > 0) {
                marginTop = '2px' // Consecutive assistant messages
              } else if (!prevMessage) {
                marginTop = '0'
              }

              return (
                <div key={`${message.id}-tool-${tcIndex}`} className="group" style={{ marginTop }}>
                  <MessageBubble message={message} isStreaming={false} singleToolCallIndex={tcIndex} />
                </div>
              )
            })

            // If message also has content, render it as a separate bubble after tool calls
            let contentBubble = null
            if (message.content && message.content.trim()) {
              const isFirstAssistant = !prevMessage || prevMessage.role !== 'assistant'
              const hasToolCallsBefore = toolCallBubbles.length > 0
              let contentMarginTop = '16px'
              if (hasToolCallsBefore) {
                contentMarginTop = '2px' // Right after tool calls
              } else if (!prevMessage) {
                contentMarginTop = '0'
              } else if (!isFirstAssistant) {
                contentMarginTop = '2px'
              }

              contentBubble = (
                <div key={`${message.id}-content`} className="group" style={{ marginTop: contentMarginTop }}>
                  <MessageBubble message={{ ...message, tool_calls: [] }} isStreaming={false} />
                </div>
              )
            }

            return [...toolCallBubbles, contentBubble]
          }

          // For user messages or assistant messages without tool_calls, render normally
          // Margin logic:
          // - Consecutive AI messages: smaller gap (2px)
          // - AI <-> User transition: larger gap (16px)
          // - Consecutive user messages: medium gap (4px)
          let marginTop = '16px'
          if (prevMessage) {
            if (prevMessage.role === 'assistant' && message.role === 'assistant') {
              marginTop = '2px'
            } else if (prevMessage.role === 'user' && message.role === 'user') {
              marginTop = '4px'
            }
          } else {
            marginTop = '0'
          }

          return (
            <div key={message.id} className="group" style={{ marginTop }}>
              <MessageBubble message={message} isStreaming={false} />
            </div>
          )
        })}

        {/* Streaming AI response - each tool call gets its own avatar like loaded messages */}
        {isStreaming && streamingToolCalls.length > 0 && streamingToolCalls.map((toolCall) => (
          <div key={toolCall.id} className="group" style={{ marginTop: '16px' }}>
            <div className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]">
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

                {/* Tool call card */}
                <div className="flex-1 min-w-0">
                  <StreamingToolCalls toolCalls={[toolCall]} />
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Streaming final content with its own avatar */}
        {isStreaming && streamingContent && (
          <div className="group" style={{ marginTop: streamingToolCalls.length > 0 ? '2px' : '16px' }}>
            <div className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]">
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

                {/* Content area */}
                <div className="flex-1 min-w-0">
                  <div className="w-full">
                    <div className="prose prose-sm max-w-none">
                      <MarkdownRenderer content={streamingContent} />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Thinking indicator - show when streaming but no content yet (after tools or initially) */}
        {isStreaming && !streamingContent && (
          <div className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]" style={{ marginTop: streamingToolCalls.length > 0 ? '12px' : '16px' }}>
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

              <div className="flex items-center gap-1.5">
                <span
                  className="rounded-full animate-bounce"
                  style={{ animationDelay: '0ms', background: 'var(--token-text-tertiary)', width: '10px', height: '10px' }}
                />
                <span
                  className="rounded-full animate-bounce"
                  style={{ animationDelay: '150ms', background: 'var(--token-text-tertiary)', width: '10px', height: '10px' }}
                />
                <span
                  className="rounded-full animate-bounce"
                  style={{ animationDelay: '300ms', background: 'var(--token-text-tertiary)', width: '10px', height: '10px' }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Scroll anchor */}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
