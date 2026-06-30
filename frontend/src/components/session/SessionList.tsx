import { useState, useRef, useEffect } from 'react'
import { Session } from '@/types'

interface SessionListProps {
  sessions: Session[]
  currentSession: Session | null
  isLoading: boolean
  onSelectSession: (session: Session) => void
  onCreateSession: () => void
  onDeleteSession: (id: string) => void
  onRenameSession: (id: string, title: string) => void
}

interface ContextMenuState {
  visible: boolean
  x: number
  y: number
  sessionId: string | null
}

export function SessionList({
  sessions,
  currentSession,
  isLoading,
  onSelectSession,
  onCreateSession,
  onDeleteSession,
  onRenameSession,
}: SessionListProps) {
  const [contextMenu, setContextMenu] = useState<ContextMenuState>({
    visible: false,
    x: 0,
    y: 0,
    sessionId: null,
  })
  const [isRenaming, setIsRenaming] = useState<string | null>(null)
  const [renameValue, setRenameValue] = useState('')
  const renameInputRef = useRef<HTMLInputElement>(null)
  const contextMenuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (contextMenuRef.current && !contextMenuRef.current.contains(e.target as Node)) {
        setContextMenu({ visible: false, x: 0, y: 0, sessionId: null })
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (isRenaming && renameInputRef.current) {
      renameInputRef.current.focus()
      renameInputRef.current.select()
    }
  }, [isRenaming])

  const handleContextMenu = (e: React.MouseEvent, session: Session) => {
    e.preventDefault()
    setContextMenu({
      visible: true,
      x: e.clientX,
      y: e.clientY,
      sessionId: session.id,
    })
  }

  const handleStartRename = () => {
    if (contextMenu.sessionId) {
      const session = sessions.find(s => s.id === contextMenu.sessionId)
      if (session) {
        setIsRenaming(session.id)
        setRenameValue(session.title || '')
        setContextMenu({ visible: false, x: 0, y: 0, sessionId: null })
      }
    }
  }

  const handleRenameSubmit = () => {
    if (isRenaming && renameValue.trim()) {
      const trimmedValue = renameValue.trim().slice(0, 100)
      onRenameSession(isRenaming, trimmedValue)
    }
    setIsRenaming(null)
    setRenameValue('')
  }

  const handleRenameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleRenameSubmit()
    } else if (e.key === 'Escape') {
      setIsRenaming(null)
      setRenameValue('')
    }
  }

  const handleDelete = () => {
    if (contextMenu.sessionId) {
      onDeleteSession(contextMenu.sessionId)
      setContextMenu({ visible: false, x: 0, y: 0, sessionId: null })
    }
  }

  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins} min ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="flex flex-col h-full">
      {/* New Chat Button - Menu Item Style */}
      <button
        onClick={onCreateSession}
        disabled={isLoading}
        className="__menu-item hoverable gap-1.5"
      >
        <span className="icon flex items-center justify-center w-6 h-6">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
        </span>
        <span className="text-sm font-medium">新对话</span>
      </button>

      {/* Session List */}
      <div className="mt-2 flex-1 overflow-y-auto min-h-0 space-y-0.5">
        {sessions.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-sm" style={{ color: 'var(--token-text-tertiary)' }}>
              暂无对话
            </p>
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = currentSession?.id === session.id
            return (
              <div
                key={session.id}
                className={`group __menu-item hoverable flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer motion-safe:transition-colors`}
                style={{
                  background: isActive ? 'var(--token-surface-tertiary)' : undefined,
                }}
                onClick={() => !isRenaming && onSelectSession(session)}
                onContextMenu={(e) => handleContextMenu(e, session)}
              >
                {/* Icon */}
                <span className="icon flex items-center justify-center w-6 h-6 shrink-0">
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    style={{ color: isActive ? 'var(--token-text-primary)' : 'var(--token-text-tertiary)' }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </span>

                {/* Text */}
                <div className="flex-1 min-w-0">
                  {isRenaming === session.id ? (
                    <input
                      ref={renameInputRef}
                      type="text"
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onBlur={handleRenameSubmit}
                      onKeyDown={handleRenameKeyDown}
                      maxLength={100}
                      className="w-full px-2 py-0.5 text-sm bg-transparent border rounded focus:outline-none"
                      style={{
                        color: 'var(--token-text-primary)',
                        borderColor: 'var(--token-border-medium)',
                      }}
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <p
                        className="text-sm truncate"
                        style={{ color: isActive ? 'var(--token-text-primary)' : 'var(--token-text-secondary)' }}
                      >
                        {session.title || 'Untitled'}
                      </p>
                      <p
                        className="text-xs truncate"
                        style={{ color: 'var(--token-text-tertiary)' }}
                      >
                        {formatRelativeTime(session.updated_at)}
                      </p>
                    </>
                  )}
                </div>

                {/* Hover Actions */}
                {!isRenaming && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-0.5">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setIsRenaming(session.id)
                        setRenameValue(session.title || '')
                      }}
                      className="rounded-lg w-9 h-9 flex items-center justify-center hover:bg-[var(--token-surface-primary)] motion-safe:transition-colors"
                      title="Rename"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        style={{ color: 'var(--token-text-tertiary)' }}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteSession(session.id)
                      }}
                      className="rounded-lg w-9 h-9 flex items-center justify-center hover:bg-red-50 motion-safe:transition-colors"
                      title="Delete"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        style={{ color: 'var(--token-text-tertiary)' }}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                    </button>
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>

      {/* Context Menu */}
      {contextMenu.visible && (
        <div
          ref={contextMenuRef}
          className="fixed z-50 rounded-xl shadow-lg py-1 min-w-[140px]"
          style={{
            left: `${contextMenu.x}px`,
            top: `${contextMenu.y}px`,
            background: 'var(--token-surface-primary)',
            border: '1px solid var(--token-border-light)',
            boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)',
          }}
        >
          <button
            onClick={handleStartRename}
            className="__menu-item hoverable gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Rename
          </button>
          <button
            onClick={handleDelete}
            className="__menu-item hoverable gap-2"
            style={{ color: 'var(--color-error)' }}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      )}
    </div>
  )
}
