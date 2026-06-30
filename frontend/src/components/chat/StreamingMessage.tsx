import { useEffect, useState } from 'react'
import { MarkdownRenderer } from './MarkdownRenderer'

interface StreamingMessageProps {
  content: string
  isComplete?: boolean
}

export function StreamingMessage({ content, isComplete = false }: StreamingMessageProps) {
  const [displayContent, setDisplayContent] = useState('')
  const [showCursor, setShowCursor] = useState(true)

  // Typewriter effect with cursor
  useEffect(() => {
    if (isComplete) {
      setDisplayContent(content)
      setShowCursor(false)
      return
    }

    // For streaming, we show content as it arrives
    setDisplayContent(content)
  }, [content, isComplete])

  // Cursor blink animation
  useEffect(() => {
    if (isComplete) return

    const interval = setInterval(() => {
      setShowCursor((prev) => !prev)
    }, 530) // Typical cursor blink rate

    return () => clearInterval(interval)
  }, [isComplete])

  return (
    <div className="w-full" style={{ paddingLeft: '44px', marginTop: '2px' }}>
      {displayContent ? (
        <div className="w-full">
          <div className="prose prose-sm max-w-none">
            <MarkdownRenderer content={displayContent} />
          </div>
          {/* Streaming cursor */}
          {!isComplete && (
            <span
              className={`inline-block w-0.5 h-4 ml-1 rounded-full align-middle ${
                showCursor ? 'opacity-100' : 'opacity-0'
              }`}
              style={{ background: 'var(--token-text-primary)' }}
            />
          )}
        </div>
      ) : (
        /* Thinking indicator */
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
      )}
    </div>
  )
}
