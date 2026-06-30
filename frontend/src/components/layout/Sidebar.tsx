import { ReactNode, useState } from 'react'

interface SidebarProps {
  children?: ReactNode
  topContent?: ReactNode
  bottomContent?: ReactNode
}

export function Sidebar({ children, topContent, bottomContent }: SidebarProps) {
  const [isExpanded, setIsExpanded] = useState(true)

  return (
    <div className="flex h-full">
      {/* Main Sidebar */}
      <div
        className={`flex flex-col h-full transition-all duration-200 ease-in-out ${isExpanded ? 'w-[var(--sidebar-width)]' : 'w-0 overflow-hidden'}`}
        style={{
          background: 'var(--token-sidebar-surface-primary)',
          borderRight: '1px solid var(--token-border-extra-light)',
        }}
      >
        {/* Top Section: New Chat button etc. */}
        {topContent && (
          <div className="p-2">
            {topContent}
          </div>
        )}

        {/* Main Content: Session list */}
        <nav className="flex-1 overflow-y-auto min-h-0">
          {children}
        </nav>

        {/* Bottom Section: Login/Settings */}
        {bottomContent && (
          <div
            className="sticky bottom-0 p-5 border-t"
            style={{
              borderColor: 'var(--token-border-extra-light)',
              background: 'var(--token-sidebar-surface-primary)',
            }}
          >
            {bottomContent}
          </div>
        )}
      </div>

      {/* Sidebar Rail - 32px narrow bar */}
      <div
        className="flex flex-col items-center py-3 shrink-0 cursor-pointer hover:bg-[var(--token-sidebar-surface-secondary)] transition-colors duration-150"
        style={{
          width: '32px',
          background: 'var(--token-sidebar-surface-primary)',
          borderRight: '1px solid var(--token-border-extra-light)',
        }}
        onClick={() => setIsExpanded(!isExpanded)}
        title={isExpanded ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        {/* Rail icon */}
        <div className="flex items-center justify-center w-6 h-6 rounded-md hover:bg-[var(--token-surface-tertiary)] transition-colors">
          <svg
            className={`w-4 h-4 transition-transform duration-200 ${isExpanded ? '' : 'rotate-180'}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            style={{ color: 'var(--token-text-secondary)' }}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M11 19l-7-7 7-7m8 14l-7-7 7-7"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
