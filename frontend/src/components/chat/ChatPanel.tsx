import { useState, useCallback, useRef } from 'react'
import { Message, ToolCallStartData, ToolCallEndData } from '@/types'
import { sseClient } from '@/utils/sse'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'

// Streaming tool call state
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

interface ChatPanelProps {
  sessionId: string | null
  messages: Message[]
  onMessagesUpdate?: (messages: Message[]) => void
  onTitleGenerated?: (sessionId: string, title: string) => void
  onCreateSession?: () => Promise<string | undefined>
}

export function ChatPanel({ sessionId, messages, onMessagesUpdate, onTitleGenerated, onCreateSession }: ChatPanelProps) {
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [streamingToolCalls, setStreamingToolCalls] = useState<StreamingToolCall[]>([])
  const abortControllerRef = useRef<AbortController | null>(null)

  const handleSend = useCallback(async (content: string, targetSessionId?: string) => {
    const effectiveSessionId = targetSessionId || sessionId
    if (!effectiveSessionId) {
      console.error('No active session')
      return
    }

    // Add user message
    const userMessage: Message = {
      id: `temp-user-${Date.now()}`,
      session_id: effectiveSessionId,
      role: 'user',
      content,
      tool_calls: [],
      created_at: new Date().toISOString(),
    }

    const updatedMessages = [...messages, userMessage]
    onMessagesUpdate?.(updatedMessages)

    // Start streaming
    setIsStreaming(true)
    setStreamingContent('')
    setStreamingToolCalls([])
    abortControllerRef.current = new AbortController()

    try {
      const generator = sseClient.streamChat(
        { message: content, session_id: effectiveSessionId },
        { signal: abortControllerRef.current.signal }
      )

      let currentContent = ''
      const finalToolCalls: StreamingToolCall[] = []

      for await (const event of generator) {
        if (event.type === 'content_delta') {
          const data = event.data as { content: string }
          currentContent += data.content
          setStreamingContent(currentContent)
        } else if (event.type === 'tool_call_start') {
          const data = event.data as ToolCallStartData
          const newToolCall: StreamingToolCall = {
            id: data.tool_call_id,
            tool_name: data.tool_name,
            arguments: data.arguments,
            status: 'running',
            result: null,
            error: null,
            startTime: new Date(),
            endTime: null,
          }
          finalToolCalls.push(newToolCall)
          setStreamingToolCalls([...finalToolCalls])
        } else if (event.type === 'tool_call_end') {
          const data = event.data as ToolCallEndData
          const toolCallIndex = finalToolCalls.findIndex(tc => tc.id === data.tool_call_id)
          if (toolCallIndex !== -1) {
            finalToolCalls[toolCallIndex] = {
              ...finalToolCalls[toolCallIndex],
              status: data.status,
              result: data.result,
              error: data.error,
              endTime: new Date(),
            }
            setStreamingToolCalls([...finalToolCalls])
          }
        } else if (event.type === 'done') {
          // done event may contain final content
          const doneData = event.data as { content?: string } | undefined
          const finalContent = doneData?.content || currentContent

          console.log('done event:', { doneData, currentContent, finalContent })

          // Create assistant message with tool calls
          const assistantToolCalls: Message['tool_calls'] = finalToolCalls.map(tc => ({
            id: tc.id,
            message_id: `temp-assistant-${Date.now()}`,
            tool_name: tc.tool_name,
            arguments: tc.arguments,
            status: tc.status,
            result: tc.result,
            error: tc.error,
            started_at: tc.startTime?.toISOString() || null,
            completed_at: tc.endTime?.toISOString() || null,
          }))

          console.log('assistantToolCalls:', assistantToolCalls.length)

          const assistantMessage: Message = {
            id: `temp-assistant-${Date.now()}`,
            session_id: effectiveSessionId,
            role: 'assistant',
            content: finalContent,
            tool_calls: assistantToolCalls.length > 0 ? assistantToolCalls : [],
            created_at: new Date().toISOString(),
          }

          console.log('assistantMessage:', { content: assistantMessage.content, tool_calls_count: assistantMessage.tool_calls?.length })

          // Final update with both messages
          onMessagesUpdate?.([...updatedMessages, assistantMessage])
          setStreamingContent('')
          setStreamingToolCalls([])
          setIsStreaming(false)

          // Generate title if this is the first message
          if (messages.length === 0 && onTitleGenerated) {
            // Auto-generate title after first exchange
            generateTitleFromMessage(effectiveSessionId, content)
          }
        } else if (event.type === 'error') {
          const data = event.data as { message: string }
          console.error('Stream error:', data.message)
          setIsStreaming(false)
        }
      }
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        console.log('Stream aborted by user')
      } else {
        console.error('Stream error:', error)
      }
      setIsStreaming(false)
    }
  }, [sessionId, messages, onMessagesUpdate, onTitleGenerated])

  const generateTitleFromMessage = async (sid: string, firstMessage: string) => {
    // Use first 50 chars of first message as title if no backend API available
    // Otherwise call the backend to generate a proper title
    try {
      const title = firstMessage.slice(0, 50).trim() + (firstMessage.length > 50 ? '...' : '')
      onTitleGenerated?.(sid, title)
    } catch (error) {
      console.error('Failed to generate title:', error)
    }
  }

  const handleStop = useCallback(() => {
    abortControllerRef.current?.abort()
    setIsStreaming(false)

    // Save partial content if any
    if (streamingContent && sessionId) {
      const assistantMessage: Message = {
        id: `temp-assistant-${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: streamingContent + '\n\n[Stopped]',
        tool_calls: [],
        created_at: new Date().toISOString(),
      }
      onMessagesUpdate?.([...messages, assistantMessage])
      setStreamingContent('')
      setStreamingToolCalls([])
    }
  }, [streamingContent, sessionId, messages, onMessagesUpdate])

  // Handle sending from welcome screen (auto-create session)
  const handleWelcomeSend = useCallback(async (content: string) => {
    if (!onCreateSession) return
    const newSessionId = await onCreateSession()
    if (newSessionId) {
      handleSend(content, newSessionId)
    }
  }, [onCreateSession, handleSend])

  // Welcome screen - ChatGPT style layout
  if (!sessionId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center" style={{ marginTop: '-140px' }}>
        {/* Centered content */}
        <div className="w-full max-w-[48rem] px-4 flex flex-col items-center">
          {/* Headline */}
          <div className="text-center" style={{ marginBottom: '25px' }}>
            <h1
              className="text-2xl leading-9 font-normal whitespace-pre-wrap"
              style={{ color: 'var(--token-text-primary)' }}
            >
              <span style={{ fontSize: '3px' }}>目标是</span>地表最强个人助理
            </h1>
          </div>

          {/* Input composer */}
          <div className="w-full">
            <ChatInput
              onSend={handleWelcomeSend}
              isStreaming={false}
              disabled={false}
              placeholder="有问题，尽管问"
              showHint={false}
              compact={true}
            />
          </div>

          {/* Footer disclaimer */}
          <div className="w-full text-center pb-3 pt-2">
            <span
              className="text-xs leading-none"
              style={{ color: 'var(--token-text-tertiary)' }}
            >
              AI 可能会产生错误信息。请核实重要内容。
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 flex flex-col h-full">
      <MessageList
        messages={messages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
        streamingToolCalls={streamingToolCalls}
      />

      <div style={{ marginTop: '24px' }}>
        <ChatInput
          onSend={handleSend}
          onStop={handleStop}
          isStreaming={isStreaming}
          disabled={!sessionId}
        />
      </div>
    </div>
  )
}
