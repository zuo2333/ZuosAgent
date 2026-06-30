import { ReactNode } from 'react'

interface HeaderProps {
  title?: string
  rightContent?: ReactNode
  onMenuClick?: () => void
}

export function Header({ title, rightContent, onMenuClick }: HeaderProps) {
  return (
    <header
      className="sticky top-0 z-30 flex items-center justify-between"
      style={{
        height: 'var(--header-height)',
        padding: '0.5rem 1rem',
        background: 'var(--token-main-surface-primary)',
        borderBottom: '1px solid var(--token-border-extra-light)',
      }}
    >
      {/* Left: Menu button (mobile) */}
      <div className="flex items-center gap-2">
        <button
          onClick={onMenuClick}
          className="flex items-center justify-center rounded-lg transition-colors hover:bg-[var(--token-surface-tertiary)]"
          style={{ width: '36px', height: '36px' }}
          title="Toggle sidebar"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            style={{ color: 'var(--token-text-secondary)' }}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>

      {/* Center: Title */}
      <div className="flex-1 text-center">
        {title && (
          <h1
            className="text-sm font-medium truncate px-4"
            style={{ color: 'var(--token-text-primary)' }}
          >
            {title}
          </h1>
        )}
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {rightContent}
      </div>
    </header>
  )
}
