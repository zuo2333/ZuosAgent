import { useState, useCallback } from 'react'

// Tool call status type
type ToolCallStatus = 'pending' | 'running' | 'success' | 'error' | 'timeout'

// Tool call data interface
interface ToolCallData {
  id: string
  tool_name: string
  arguments: Record<string, unknown>
  status: ToolCallStatus
  result: string | null
  error: string | null
  started_at: string | null
  completed_at: string | null
}

// Tool icon mapping
const TOOL_ICONS: Record<string, React.ReactNode> = {
  web_search: (
    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
    </svg>
  ),
  db_query: (
    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
    </svg>
  ),
}

// Tool display name mapping
const TOOL_NAMES: Record<string, string> = {
  web_search: 'Web Search',
  db_query: 'Database Query',
}

// Status configuration
const STATUS_CONFIG: Record<ToolCallStatus, { label: string; bgColor: string; textColor: string; dotColor: string }> = {
  pending: { label: 'Pending', bgColor: '#f3f4f6', textColor: '#6b7280', dotColor: '#9ca3af' },
  running: { label: 'Running', bgColor: '#eff6ff', textColor: '#2563eb', dotColor: '#3b82f6' },
  success: { label: 'SUCCESS', bgColor: '#e8f8ef', textColor: '#16a34a', dotColor: '#22c55e' },
  error: { label: 'FAILED', bgColor: '#fef2f2', textColor: '#dc2626', dotColor: '#ef4444' },
  timeout: { label: 'TIMEOUT', bgColor: '#fffbeb', textColor: '#d97706', dotColor: '#f59e0b' },
}

interface ToolCallCardProps {
  toolCall: ToolCallData
  defaultExpanded?: boolean
}

export function ToolCallCard({ toolCall, defaultExpanded = false }: ToolCallCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded)

  const toggleExpanded = useCallback(() => {
    setIsExpanded((prev) => !prev)
  }, [])

  const icon = TOOL_ICONS[toolCall.tool_name] || (
    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  )
  const displayName = TOOL_NAMES[toolCall.tool_name] || toolCall.tool_name
  const statusConfig = STATUS_CONFIG[toolCall.status]

  // Calculate duration
  const duration = toolCall.started_at && toolCall.completed_at
    ? Math.round((new Date(toolCall.completed_at).getTime() - new Date(toolCall.started_at).getTime()) / 1000)
    : null

  // Parse result
  const parseResult = (result: string | null): { type: 'json' | 'text' | 'list'; data: unknown; count?: number } => {
    if (!result) return { type: 'text', data: null }
    try {
      const parsed = JSON.parse(result)
      if (Array.isArray(parsed)) {
        return { type: 'list', data: parsed, count: parsed.length }
      }
      return { type: 'json', data: parsed }
    } catch {
      return { type: 'text', data: result }
    }
  }

  const resultInfo = parseResult(toolCall.result)

  return (
    <div
      className="my-1.5"
      style={{
        background: '#ffffff',
        borderRadius: '12px',
        border: '1px solid #e6e6e6',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        padding: '10px 12px',
        width: 'fit-content',
        maxWidth: '100%',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: '16px',
        }}
      >
        {/* Left: Icon + Name + Duration */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          {/* Tool Icon */}
          <div
            style={{
              width: '20px',
              height: '20px',
              background: '#f2f4f7',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#333',
            }}
          >
            {icon}
          </div>

          {/* Tool Name */}
          <span
            style={{
              fontSize: '14px',
              fontWeight: 500,
              color: '#333',
            }}
          >
            {displayName}
          </span>

          {/* Duration */}
          {duration !== null && (
            <span
              style={{
                fontSize: '13px',
                color: '#999',
              }}
            >
              {duration}s
            </span>
          )}
        </div>

        {/* Right: Status Badge */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: statusConfig.bgColor,
            color: statusConfig.textColor,
            fontSize: '11px',
            padding: '3px 10px',
            borderRadius: '999px',
            minWidth: '60px',
            justifyContent: 'center',
          }}
        >
          {/* Status Dot */}
          {toolCall.status === 'running' ? (
            <svg className="w-1.5 h-1.5 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
          ) : (
            <div
              style={{
                width: '5px',
                height: '5px',
                background: statusConfig.dotColor,
                borderRadius: '50%',
                marginRight: '0px',
              }}
            />
          )}
          {statusConfig.label}
        </div>
      </div>

      {/* Parameters - inline format */}
      <div
        style={{
          marginTop: '6px',
          background: '#f7f8fa',
          borderRadius: '6px',
          padding: '6px 10px',
          fontSize: '12px',
          color: '#666',
          fontFamily: 'monospace',
        }}
      >
        {Object.entries(toolCall.arguments).map(([key, value], index) => (
          <span key={key}>
            {index > 0 && ', '}
            <span style={{ color: '#888' }}>{key}</span>=
            <span style={{ color: '#333' }}>"{String(value)}"</span>
          </span>
        ))}
      </div>

      {/* Error Display */}
      {toolCall.status === 'error' && toolCall.error && (
        <div
          style={{
            marginTop: '6px',
            background: '#fef2f2',
            borderRadius: '6px',
            padding: '6px 10px',
            border: '1px solid #fecaca',
            fontSize: '12px',
            color: '#dc2626',
          }}
        >
          {toolCall.error}
        </div>
      )}

      {/* Timeout Message */}
      {toolCall.status === 'timeout' && (
        <div
          style={{
            marginTop: '6px',
            background: '#fffbeb',
            borderRadius: '6px',
            padding: '6px 10px',
            fontSize: '12px',
            color: '#d97706',
          }}
        >
          Tool execution timed out.
        </div>
      )}

      {/* Result Section - Expandable */}
      {(toolCall.status === 'success' || toolCall.result) && (
        <div style={{ marginTop: '6px' }}>
          <button
            onClick={toggleExpanded}
            style={{
              background: 'transparent',
              border: 'none',
              borderRadius: '4px',
              padding: '4px 8px',
              fontSize: '12px',
              cursor: 'pointer',
              color: '#666',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = '#f3f4f6'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'transparent'
            }}
          >
            <svg
              style={{
                width: '12px',
                height: '12px',
                transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)',
                transition: 'transform 0.2s',
              }}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            {isExpanded ? 'Hide' : 'Result'}
            {resultInfo.count !== undefined && (
              <span style={{ color: '#999' }}>({resultInfo.count})</span>
            )}
          </button>

          {isExpanded && (
            <div
              style={{
                marginTop: '6px',
                background: '#f7f8fa',
                borderRadius: '8px',
                padding: '8px 10px',
                maxHeight: '200px',
                overflowY: 'auto',
                fontSize: '12px',
              }}
            >
              {resultInfo.type === 'list' && Array.isArray(resultInfo.data) ? (
                <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                  {resultInfo.data.map((item, index) => (
                    <li
                      key={index}
                      style={{
                        color: '#333',
                        paddingBottom: '6px',
                        marginBottom: '6px',
                        borderBottom: index < (resultInfo.data as unknown[]).length - 1 ? '1px solid #e6e6e6' : 'none',
                      }}
                    >
                      {typeof item === 'object' ? (
                        <div>
                          {item.title && (
                            <div style={{ fontWeight: 500, marginBottom: '2px' }}>
                              {String(item.title)}
                            </div>
                          )}
                          {item.url && (
                            <a
                              href={String(item.url)}
                              target="_blank"
                              rel="noopener noreferrer"
                              style={{ color: '#2563eb', fontSize: '11px' }}
                            >
                              {String(item.url)}
                            </a>
                          )}
                          {item.snippet && (
                            <p style={{ color: '#666', fontSize: '11px', marginTop: '2px', margin: '2px 0 0 0' }}>
                              {String(item.snippet)}
                            </p>
                          )}
                          {!item.title && !item.url && !item.snippet && (
                            <pre style={{ fontFamily: 'monospace', fontSize: '11px', margin: 0 }}>
                              {JSON.stringify(item, null, 2)}
                            </pre>
                          )}
                        </div>
                      ) : (
                        <span>{String(item)}</span>
                      )}
                    </li>
                  ))}
                </ul>
              ) : resultInfo.type === 'json' ? (
                <pre style={{ fontFamily: 'monospace', fontSize: '11px', color: '#333', margin: 0, whiteSpace: 'pre-wrap' }}>
                  {JSON.stringify(resultInfo.data, null, 2)}
                </pre>
              ) : (
                <p style={{ color: '#666', margin: 0, whiteSpace: 'pre-wrap' }}>
                  {String(resultInfo.data)}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ToolCallCard
