import {
  SSEEvent,
  ContentDeltaData,
  ToolCallStartData,
  ToolCallEndData,
  ErrorData
} from '@/types'

type SSEEventType = SSEEvent['type']
type EventHandler<T = unknown> = (data: T) => void

interface SSEOptions {
  onContentDelta?: EventHandler<ContentDeltaData>
  onToolCallStart?: EventHandler<ToolCallStartData>
  onToolCallEnd?: EventHandler<ToolCallEndData>
  onDone?: EventHandler<void>
  onError?: EventHandler<ErrorData>
  signal?: AbortSignal
}

interface ChatRequest {
  message: string
  session_id: string
  stream?: boolean
}

/**
 * SSE Client for streaming chat responses
 * Supports multiple event types: content_delta, tool_call_start, tool_call_end, done, error
 */
export class SSEClient {
  private controller: AbortController | null = null

  /**
   * Stream chat messages from the server
   * Returns an async generator that yields SSE events
   */
  async *streamChat(request: ChatRequest, options?: SSEOptions): AsyncGenerator<SSEEvent> {
    this.controller = new AbortController()
    const signal = options?.signal || this.controller.signal

    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
      },
      body: JSON.stringify({
        ...request,
        stream: true,
      }),
      signal,
    })

    if (!response.ok) {
      const error: ErrorData = await response.json().catch(() => ({
        message: `HTTP Error: ${response.status}`,
      }))
      options?.onError?.(error)
      throw new Error(error.message)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Response body is not readable')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    try {
      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        buffer += decoder.decode(value, { stream: true })

        // Process complete events from buffer
        const events = this.parseEvents(buffer)
        buffer = events.remainingBuffer

        for (const event of events.parsed) {
          // Call specific handlers
          this.callHandler(event, options)

          yield event
        }
      }
    } finally {
      reader.releaseLock()
    }
  }

  /**
   * Stream chat with callback-based API
   */
  async streamChatWithCallbacks(request: ChatRequest, options: SSEOptions): Promise<void> {
    for await (const _event of this.streamChat(request, options)) {
      // Events are already handled via callbacks in streamChat
    }
  }

  /**
   * Abort the current stream
   */
  abort(): void {
    this.controller?.abort()
    this.controller = null
  }

  /**
   * Check if stream is active
   */
  isStreaming(): boolean {
    return this.controller !== null && !this.controller.signal.aborted
  }

  private parseEvents(buffer: string): { parsed: SSEEvent[]; remainingBuffer: string } {
    const events: SSEEvent[] = []
    let remaining = buffer

    // SSE format: "event: <type>\ndata: <json>\n\n"
    const eventPattern = /event:\s*(\w+)\ndata:\s*(.+?)\n\n/gs

    let match
    let lastIndex = 0

    while ((match = eventPattern.exec(buffer)) !== null) {
      lastIndex = match.index + match[0].length
      const eventType = match[1] as SSEEventType
      const dataStr = match[2]

      try {
        const data = JSON.parse(dataStr)
        events.push({ type: eventType, data })
      } catch {
        // If JSON parsing fails, create a raw event
        events.push({ type: eventType, data: dataStr })
      }
    }

    // Keep any incomplete data in buffer
    if (lastIndex > 0) {
      remaining = buffer.slice(lastIndex)
    }

    return { parsed: events, remainingBuffer: remaining }
  }

  private callHandler(event: SSEEvent, options?: SSEOptions): void {
    if (!options) return

    switch (event.type) {
      case 'content_delta':
        options.onContentDelta?.(event.data as ContentDeltaData)
        break
      case 'tool_call_start':
        options.onToolCallStart?.(event.data as ToolCallStartData)
        break
      case 'tool_call_end':
        options.onToolCallEnd?.(event.data as ToolCallEndData)
        break
      case 'done':
        options.onDone?.()
        break
      case 'error':
        options.onError?.(event.data as ErrorData)
        break
    }
  }
}

// Export singleton instance
export const sseClient = new SSEClient()

// Export utility function for simple streaming
export async function* streamChat(
  message: string,
  sessionId: string,
  signal?: AbortSignal
): AsyncGenerator<SSEEvent> {
  const client = new SSEClient()
  yield* client.streamChat(
    { message, session_id: sessionId },
    { signal }
  )
}
