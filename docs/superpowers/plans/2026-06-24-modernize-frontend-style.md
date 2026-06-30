# Modernize Frontend Style Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the frontend from complex glassmorphism design to a clean, modern, minimalist style with light translucent sidebar, larger border-radius, and simplified animations.

**Architecture:** CSS-first styling approach using Tailwind CSS + CSS variables. Changes are purely cosmetic - no functional changes to components or state management.

**Tech Stack:** React 18, TypeScript, Tailwind CSS, Vite

## Global Constraints

- Border-radius range: 16-28px (no smaller values)
- Sidebar must use light glass effect (white/light gray), NOT dark background
- Background: soft single gradient, NO floating orb animations
- Spacing: increase by 20-30% from current values
- Preserve all existing functionality - visual changes only
- No new dependencies
- Light theme only (no dark mode support)

---

## Task 1: Update CSS Variables System

**Files:**
- Modify: `frontend/src/index.css`

**Interfaces:**
- Produces: Updated CSS custom properties that all components consume

### 1.1 Update Border-Radius Variables

- [ ] **Step 1: Update border-radius CSS variables**

Edit `frontend/src/index.css` lines 62-68:

```css
  /* Border Radius */
  --radius-sm: 0.5rem;
  --radius-md: 0.75rem;
  --radius-lg: 1rem;
  --radius-xl: 1.5rem;
  --radius-2xl: 2rem;
  --radius-full: 9999px;
```

- [ ] **Step 2: Verify CSS compiles**

Run: `cd frontend && npm run build`
Expected: Build succeeds without CSS errors

### 1.2 Simplify Background Styles

- [ ] **Step 3: Remove floating orb animation keyframes**

Delete from `frontend/src/index.css` lines 121-149 (the `float` and `pulse-glow` keyframes):

```css
/* DELETE these keyframes:
@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -30px) scale(1.05);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.95);
  }
}

@keyframes pulse-glow {
  0%, 100% {
    opacity: 0.6;
  }
  50% {
    opacity: 0.8;
  }
}
*/
```

- [ ] **Step 4: Simplify body background**

Edit `frontend/src/index.css` lines 105-112:

```css
body {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
  color: var(--color-gray-900);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
  line-height: 1.6;
  overflow: hidden;
}
```

- [ ] **Step 5: Verify CSS compiles**

Run: `cd frontend && npm run build`
Expected: Build succeeds

### 1.3 Update Glass Effect Variables

- [ ] **Step 6: Update glass effect variables for light theme**

Edit `frontend/src/index.css` lines 77-81:

```css
  /* Glass Effect */
  --glass-blur: blur(12px);
  --glass-border: 1px solid rgba(0, 0, 0, 0.06);
  --glass-border-subtle: 1px solid rgba(0, 0, 0, 0.04);
  --glass-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
```

- [ ] **Step 7: Update surface variables**

Edit `frontend/src/index.css` lines 23-27:

```css
  /* Surface - Glass Effect */
  --surface-glass: rgba(255, 255, 255, 0.85);
  --surface-card: rgba(255, 255, 255, 0.92);
  --surface-overlay: rgba(255, 255, 255, 0.96);
  --surface-solid: #ffffff;
```

- [ ] **Step 8: Verify CSS compiles**

Run: `cd frontend && npm run build`
Expected: Build succeeds

### 1.4 Update Spacing Variables

- [ ] **Step 9: Update spacing variables**

Edit `frontend/src/index.css` lines 51-61:

```css
  /* Spacing */
  --space-1: 0.3rem;
  --space-2: 0.6rem;
  --space-3: 0.9rem;
  --space-4: 1.2rem;
  --space-5: 1.5rem;
  --space-6: 1.8rem;
  --space-8: 2.4rem;
  --space-10: 3rem;
  --space-12: 3.6rem;
```

- [ ] **Step 10: Verify CSS compiles**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 11: Commit CSS variable changes**

```bash
git add frontend/src/index.css
git commit -m "style: update CSS variables for modern minimalist design

- Increase border-radius range to 16-28px
- Simplify background to soft gradient
- Update glass effect for light theme
- Remove floating orb animation keyframes
- Increase spacing by 20%"
```

---

## Task 2: Update Layout Components

**Files:**
- Modify: `frontend/src/components/layout/AppLayout.tsx`
- Modify: `frontend/src/components/layout/Sidebar.tsx`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: Simplified layout with light sidebar

### 2.1 Remove Floating Orbs from AppLayout

- [ ] **Step 1: Simplify AppLayout background**

Replace entire `frontend/src/components/layout/AppLayout.tsx`:

```tsx
import { ReactNode } from 'react'

interface AppLayoutProps {
  sidebarContent?: ReactNode
  children: ReactNode
}

export function AppLayout({ sidebarContent, children }: AppLayoutProps) {
  return (
    <div className="relative flex h-screen w-screen overflow-hidden">
      {/* Content Layer */}
      <div className="relative flex h-full w-full">
        {/* Sidebar */}
        <aside
          className="w-72 flex flex-col h-full"
          style={{
            background: 'rgba(255, 255, 255, 0.92)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            borderRight: '1px solid rgba(0, 0, 0, 0.06)',
          }}
        >
          {sidebarContent}
        </aside>

        {/* Main Content */}
        <main className="flex-1 flex flex-col h-full">
          {children}
        </main>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

### 2.2 Update Sidebar to Light Theme

- [ ] **Step 3: Update Sidebar component**

Replace entire `frontend/src/components/layout/Sidebar.tsx`:

```tsx
import { ReactNode } from 'react'

interface SidebarProps {
  children?: ReactNode
}

export function Sidebar({ children }: SidebarProps) {
  return (
    <aside
      className="w-72 flex flex-col h-full"
      style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
      }}
    >
      {/* Logo Area */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div
            className="w-9 h-9 rounded-xl flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, var(--color-primary-500), var(--color-primary-600))',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
            }}
          >
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900 tracking-tight">LLM Chat</h1>
            <p className="text-xs text-gray-500">AI Assistant</p>
          </div>
        </div>
      </div>

      {/* Navigation Content */}
      <nav className="flex-1 overflow-y-auto py-3 px-3">
        {children}
      </nav>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-100">
        <p className="text-xs text-gray-400 text-center">
          Powered by AI
        </p>
      </div>
    </aside>
  )
}
```

- [ ] **Step 4: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 5: Commit layout changes**

```bash
git add frontend/src/components/layout/AppLayout.tsx frontend/src/components/layout/Sidebar.tsx
git commit -m "style: simplify layout and update sidebar to light theme

- Remove floating orb decorations from AppLayout
- Simplify background to solid light color
- Update Sidebar to light glass effect with proper text colors"
```

---

## Task 3: Update Chat Components

**Files:**
- Modify: `frontend/src/components/chat/ChatInput.tsx`
- Modify: `frontend/src/components/chat/MessageBubble.tsx`
- Modify: `frontend/src/components/chat/MessageList.tsx`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: Chat UI with larger border-radius and cleaner styling

### 3.1 Update ChatInput Component

- [ ] **Step 1: Update ChatInput with larger border-radius**

Replace entire `frontend/src/components/chat/ChatInput.tsx`:

```tsx
import { useState, useRef, useEffect, useCallback } from 'react'

interface ChatInputProps {
  onSend: (message: string) => void
  onStop?: () => void
  isStreaming?: boolean
  disabled?: boolean
  placeholder?: string
}

export function ChatInput({
  onSend,
  onStop,
  isStreaming = false,
  disabled = false,
  placeholder = 'Type your message...',
}: ChatInputProps) {
  const [message, setMessage] = useState('')
  const [isFocused, setIsFocused] = useState(false)
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
      className="p-5"
      style={{
        background: 'linear-gradient(to top, rgba(248,250,252,0.98) 0%, rgba(248,250,252,0.95) 100%)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderTop: '1px solid rgba(0, 0, 0, 0.04)',
      }}
    >
      <div className="max-w-3xl mx-auto">
        <div
          className="flex items-end gap-3 p-3 transition-all duration-200"
          style={{
            background: isFocused ? 'rgba(255, 255, 255, 1)' : 'rgba(255, 255, 255, 0.9)',
            boxShadow: isFocused
              ? '0 0 0 2px rgba(14, 165, 233, 0.15), 0 4px 16px rgba(0, 0, 0, 0.04)'
              : '0 2px 8px rgba(0, 0, 0, 0.03)',
            border: isFocused ? '1px solid rgba(14, 165, 233, 0.2)' : '1px solid rgba(0, 0, 0, 0.06)',
            borderRadius: '24px',
          }}
        >
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsFocused(true)}
              onBlur={() => setIsFocused(false)}
              disabled={disabled}
              placeholder={placeholder}
              rows={1}
              className="w-full resize-none bg-transparent px-4 py-3 text-gray-900 placeholder-gray-400 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
              style={{ minHeight: '48px', maxHeight: '200px' }}
            />
          </div>

          {isStreaming ? (
            <button
              onClick={handleStop}
              className="flex items-center justify-center w-12 h-12 transition-all duration-200 hover:scale-105"
              style={{
                background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                boxShadow: '0 4px 12px rgba(239, 68, 68, 0.25)',
                borderRadius: '16px',
              }}
              title="Stop generating"
            >
              <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
                <rect x="6" y="6" width="12" height="12" rx="2" />
              </svg>
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!message.trim() || disabled}
              className="flex items-center justify-center w-12 h-12 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed hover:scale-105 disabled:hover:scale-100"
              style={{
                background: message.trim() && !disabled
                  ? 'linear-gradient(135deg, #0ea5e9, #0284c7)'
                  : 'linear-gradient(135deg, #e2e8f0, #cbd5e1)',
                boxShadow: message.trim() && !disabled
                  ? '0 4px 12px rgba(14, 165, 233, 0.25)'
                  : 'none',
                borderRadius: '16px',
              }}
              title="Send message (Enter)"
            >
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          )}
        </div>

        <p className="text-center text-xs text-gray-400 mt-3 opacity-70">
          <kbd className="px-1.5 py-0.5 bg-gray-100 rounded text-gray-500 font-mono">Shift + Enter</kbd>
          <span className="mx-1"> for new line</span>
        </p>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

### 3.2 Update MessageBubble Component

- [ ] **Step 3: Update MessageBubble with larger border-radius**

Replace entire `frontend/src/components/chat/MessageBubble.tsx`:

```tsx
import { useState, useCallback } from 'react'
import { Message } from '@/types'
import { MarkdownRenderer } from './MarkdownRenderer'
import { ToolCallCard } from './ToolCallCard'

interface MessageBubbleProps {
  message: Message
  isStreaming?: boolean
}

export function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'
  const hasToolCalls = message.tool_calls && message.tool_calls.length > 0

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      console.error('Failed to copy message')
    }
  }, [message.content])

  return (
    <div
      className={`flex gap-4 mb-6 animate-fade-in-up ${isUser ? 'flex-row-reverse' : ''}`}
      style={{ animationDelay: '50ms' }}
    >
      {/* Avatar */}
      <div
        className={`flex-shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center text-sm font-medium ${
          isUser
            ? 'bg-gradient-to-br from-sky-500 to-blue-600 text-white'
            : 'bg-gradient-to-br from-gray-100 to-gray-200 text-gray-600'
        }`}
        style={{ boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04)' }}
      >
        {isUser ? (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        ) : (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        )}
      </div>

      {/* Message Content */}
      <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
        <div className={`relative max-w-[85%] group`}>
          {hasToolCalls && !isUser && (
            <div className="mb-3 space-y-2">
              {message.tool_calls.map((toolCall) => (
                <ToolCallCard key={toolCall.id} toolCall={toolCall} />
              ))}
            </div>
          )}

          {(message.content || isStreaming) && (
            <div
              className={`px-5 py-4 ${
                isUser
                  ? 'rounded-3xl rounded-br-lg text-white'
                  : 'rounded-3xl rounded-bl-lg'
              }`}
              style={isUser ? {
                background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
                boxShadow: '0 4px 16px rgba(14, 165, 233, 0.15)',
                borderRadius: '24px 24px 8px 24px',
              } : {
                background: 'rgba(255, 255, 255, 0.95)',
                backdropFilter: 'blur(8px)',
                WebkitBackdropFilter: 'blur(8px)',
                border: '1px solid rgba(0, 0, 0, 0.04)',
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.03)',
                borderRadius: '24px 24px 24px 8px',
              }}
            >
              {isUser ? (
                <p className="whitespace-pre-wrap break-words leading-relaxed">{message.content}</p>
              ) : (
                <div className="text-gray-700 leading-relaxed">
                  <MarkdownRenderer content={message.content} />
                </div>
              )}

              {isStreaming && !isUser && (
                <span
                  className="inline-block w-0.5 h-4 ml-1 rounded-full"
                  style={{
                    background: 'linear-gradient(180deg, #0ea5e9, #38bdf8)',
                    animation: 'pulse 1s ease-in-out infinite',
                  }}
                />
              )}
            </div>
          )}

          {!isUser && !isStreaming && (message.content || hasToolCalls) && (
            <button
              onClick={handleCopy}
              className="absolute -bottom-1 right-2 p-1.5 rounded-xl opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-gray-100"
              style={{
                background: copied ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 255, 255, 0.95)',
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.04)',
              }}
              title="Copy message"
            >
              {copied ? (
                <svg className="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              )}
            </button>
          )}

          <div
            className={`text-xs mt-2 px-1 ${isUser ? 'text-sky-200' : 'text-gray-400'}`}
          >
            {new Date(message.created_at).toLocaleTimeString([], {
              hour: '2-digit',
              minute: '2-digit',
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

### 3.3 Update MessageList Component

- [ ] **Step 5: Update MessageList with better spacing**

Replace entire `frontend/src/components/chat/MessageList.tsx`:

```tsx
import { useEffect, useRef } from 'react'
import { Message } from '@/types'
import { MessageBubble } from './MessageBubble'
import { StreamingMessage } from './StreamingMessage'

interface MessageListProps {
  messages: Message[]
  streamingContent?: string
  isStreaming?: boolean
}

export function MessageList({ messages, streamingContent, isStreaming = false }: MessageListProps) {
  const listRef = useRef<HTMLDivElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center text-gray-500">
          <div
            className="w-20 h-20 mx-auto mb-6 rounded-2xl flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.08), rgba(56, 189, 248, 0.04))',
              border: '1px solid rgba(14, 165, 233, 0.1)',
            }}
          >
            <svg
              className="w-10 h-10 text-sky-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-medium text-gray-800 mb-2">Start a conversation</h2>
          <p className="text-gray-400">Send a message to begin chatting</p>
        </div>
      </div>
    )
  }

  return (
    <div
      ref={listRef}
      className="flex-1 overflow-y-auto px-6 py-8"
    >
      <div className="max-w-3xl mx-auto space-y-2">
        {messages.map((message) => (
          <div key={message.id} className="group">
            <MessageBubble message={message} isStreaming={false} />
          </div>
        ))}

        {isStreaming && streamingContent !== undefined && (
          <StreamingMessage content={streamingContent} isComplete={false} />
        )}

        <div ref={bottomRef} />
      </div>
    </div>
  )
}
```

- [ ] **Step 6: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 7: Commit chat component changes**

```bash
git add frontend/src/components/chat/ChatInput.tsx frontend/src/components/chat/MessageBubble.tsx frontend/src/components/chat/MessageList.tsx
git commit -m "style: update chat components with modern minimalist design

- Increase border-radius to 24px for input and bubbles
- Simplify shadows and gradients
- Improve spacing and padding
- Update empty state styling"
```

---

## Task 4: Update Session Components

**Files:**
- Modify: `frontend/src/components/session/SessionList.tsx`

**Interfaces:**
- Consumes: CSS variables from Task 1
- Produces: Session list with light theme styling

### 4.1 Update SessionList Component

- [ ] **Step 1: Update SessionList for light theme**

Replace entire `frontend/src/components/session/SessionList.tsx`:

```tsx
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
      <button
        onClick={onCreateSession}
        disabled={isLoading}
        className="w-full py-3 rounded-2xl font-medium transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.02] active:scale-[0.98]"
        style={{
          background: 'linear-gradient(135deg, #0ea5e9, #0284c7)',
          boxShadow: '0 4px 12px rgba(14, 165, 233, 0.2)',
          borderRadius: '16px',
        }}
      >
        <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
        <span className="text-white">New Chat</span>
      </button>

      <div className="mt-4 flex-1 overflow-y-auto space-y-1.5">
        {sessions.length === 0 ? (
          <div className="text-center py-12">
            <div
              className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center"
              style={{ background: 'rgba(14, 165, 233, 0.06)' }}
            >
              <svg
                className="w-8 h-8 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            </div>
            <p className="text-gray-500 text-sm font-medium">No conversations</p>
            <p className="text-gray-400 text-xs mt-1">Start a new chat to begin</p>
          </div>
        ) : (
          sessions.map((session) => {
            const isActive = currentSession?.id === session.id
            return (
              <div
                key={session.id}
                className={`group relative flex items-start p-3 rounded-2xl cursor-pointer transition-all duration-200 ${
                  isActive ? 'scale-[1.02]' : 'hover:scale-[1.01]'
                }`}
                style={{
                  background: isActive
                    ? 'linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(56, 189, 248, 0.06))'
                    : 'transparent',
                  border: isActive ? '1px solid rgba(14, 165, 233, 0.2)' : '1px solid transparent',
                  borderRadius: '16px',
                }}
                onClick={() => !isRenaming && onSelectSession(session)}
                onContextMenu={(e) => handleContextMenu(e, session)}
              >
                {isActive && (
                  <div
                    className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 rounded-full"
                    style={{ background: 'linear-gradient(180deg, #0ea5e9, #38bdf8)' }}
                  />
                )}

                <div
                  className={`w-9 h-9 rounded-xl flex items-center justify-center mr-3 flex-shrink-0 transition-colors ${
                    isActive ? 'text-sky-500' : 'text-gray-400'
                  }`}
                  style={{
                    background: isActive ? 'rgba(14, 165, 233, 0.1)' : 'rgba(0, 0, 0, 0.04)',
                    borderRadius: '12px',
                  }}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                    />
                  </svg>
                </div>

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
                      className="w-full px-3 py-1.5 text-sm bg-white text-gray-900 border border-sky-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-sky-200"
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <p
                        className={`text-sm font-medium truncate ${
                          isActive ? 'text-gray-900' : 'text-gray-600'
                        }`}
                      >
                        {session.title || 'Untitled'}
                      </p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {formatRelativeTime(session.updated_at)}
                      </p>
                    </>
                  )}
                </div>

                {!isRenaming && (
                  <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setIsRenaming(session.id)
                        setRenameValue(session.title || '')
                      }}
                      className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Rename"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onDeleteSession(session.id)
                      }}
                      className="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition-colors"
                      title="Delete"
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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

      {contextMenu.visible && (
        <div
          ref={contextMenuRef}
          className="fixed z-50 rounded-2xl shadow-xl py-1 min-w-[140px]"
          style={{
            left: `${contextMenu.x}px`,
            top: `${contextMenu.y}px`,
            background: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(0, 0, 0, 0.06)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.08)',
          }}
        >
          <button
            onClick={handleStartRename}
            className="w-full px-4 py-2.5 text-left text-sm text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            Rename
          </button>
          <button
            onClick={handleDelete}
            className="w-full px-4 py-2.5 text-left text-sm text-red-500 hover:bg-red-50 hover:text-red-600 transition-colors flex items-center gap-2"
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
```

- [ ] **Step 2: Verify app builds**

Run: `cd frontend && npm run build`
Expected: Build succeeds

- [ ] **Step 3: Commit session component changes**

```bash
git add frontend/src/components/session/SessionList.tsx
git commit -m "style: update SessionList for light theme design

- Adapt all colors for light theme
- Increase border-radius to 16px
- Update hover and active states
- Update context menu styling
- Improve spacing and typography"
```

---

## Task 5: Verification and Testing

**Files:**
- Test: Visual verification in browser

**Interfaces:**
- Consumes: All previous tasks

### 5.1 Start Development Server

- [ ] **Step 1: Start frontend development server**

Run: `cd frontend && npm run dev`
Expected: Server starts at http://localhost:5173

- [ ] **Step 2: Open browser and verify**

Open: http://localhost:5173
Verify:
- [ ] Background is soft light gradient (no floating orbs)
- [ ] Sidebar is light/white glass effect
- [ ] All text in sidebar is readable (dark on light)
- [ ] New Chat button has correct styling
- [ ] Input field has 24px border-radius
- [ ] Message bubbles have larger border-radius (24px)
- [ ] All hover effects work correctly
- [ ] Empty state looks correct

### 5.2 Test Responsive Layout

- [ ] **Step 3: Test different screen sizes**

Resize browser window to test:
- [ ] Mobile width (375px) - layout adapts
- [ ] Tablet width (768px) - sidebar visible
- [ ] Desktop width (1280px+) - full layout

### 5.3 Test Interactions

- [ ] **Step 4: Test all interactive elements**

Test each interaction:
- [ ] Create new session button - hover scale effect
- [ ] Select session - active state highlight
- [ ] Rename session - input field appears
- [ ] Delete session - context menu shows
- [ ] Input focus - border highlight
- [ ] Send message - button hover scale
- [ ] Message hover - copy button appears
- [ ] Scroll message list - smooth scrolling

### 5.4 Final Commit

- [ ] **Step 5: Create final verification commit**

```bash
git add -A
git commit -m "style: complete frontend modernization

All visual changes implemented:
- Simplified background with soft gradient
- Light glass effect sidebar
- Increased border-radius (16-28px range)
- Improved spacing throughout
- Removed decorative animations
- All functionality preserved"
```

---

## Summary

| Task | Description | Files Modified |
|------|-------------|----------------|
| 1 | CSS Variables System | `index.css` |
| 2 | Layout Components | `AppLayout.tsx`, `Sidebar.tsx` |
| 3 | Chat Components | `ChatInput.tsx`, `MessageBubble.tsx`, `MessageList.tsx` |
| 4 | Session Components | `SessionList.tsx` |
| 5 | Verification | Manual testing |

**Total commits:** 5 (one per task)
