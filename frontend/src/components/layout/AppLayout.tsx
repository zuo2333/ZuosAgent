import { ReactNode } from 'react'

interface AppLayoutProps {
  sidebarContent?: ReactNode
  sidebarBottomContent?: ReactNode
  headerTitle?: string
  headerContent?: ReactNode
  children: ReactNode
}

export function AppLayout({
  sidebarContent,
  sidebarBottomContent,
  headerTitle,
  headerContent,
  children,
}: AppLayoutProps) {
  return (
    <div className="flex h-svh w-screen flex-col">
      {/* Main Area */}
      <div className="relative z-0 flex min-h-0 w-full flex-1">
        {/* Sidebar */}
        <aside
          className="flex flex-col h-full shrink-0"
          style={{
            width: 'var(--sidebar-width)',
            background: 'var(--token-sidebar-surface-primary)',
            borderRight: '1px solid var(--token-border-extra-light)',
          }}
        >
          {/* Sidebar Header with Logo - aligned with menu items */}
          <div
            className="flex items-center shrink-0"
            style={{
              height: 'var(--header-height)',
              background: 'var(--token-sidebar-surface-primary)',
              padding: '0.5rem 0.75rem', // Same as __menu-item padding
            }}
          >
            {/* Logo - same size as menu item icons (w-6 h-6) */}
            <a
              href="/"
              className="flex items-center justify-center rounded-lg transition-colors hover:bg-[var(--token-surface-hover)]"
              style={{ width: '24px', height: '24px' }}
              title="主页"
            >
              <div
                className="w-6 h-6 rounded-full bg-cover bg-center"
                style={{
                  backgroundImage: 'url(/logo.jpg)',
                }}
              />
            </a>
          </div>

          {/* Top Section: New Chat button etc. */}
          <div className="shrink-0 p-2">
            {sidebarContent}
          </div>

          {/* Spacer to push bottom content down */}
          <div className="flex-1" />

          {/* Bottom Section: Login/Settings - fixed at bottom */}
          {sidebarBottomContent && (
            <div
              className="shrink-0 border-t"
              style={{
                padding: '12px 12px 20px 12px',
                borderColor: 'var(--token-border-extra-light)',
                background: 'var(--token-sidebar-surface-primary)',
              }}
            >
              {sidebarBottomContent}
            </div>
          )}
        </aside>

        {/* Content Area */}
        <div className="flex-1 flex flex-col h-full min-w-0">
          {/* Header */}
          <header
            className="sticky top-0 z-30 flex items-center justify-between shrink-0"
            style={{
              height: 'var(--header-height)',
              padding: '0.5rem 1rem',
              background: 'var(--token-main-surface-primary)',
              borderBottom: '1px solid var(--token-border-extra-light)',
            }}
          >
            {/* Left: Menu button (for mobile) */}
            <div className="flex items-center gap-2">
              <button
                className="flex items-center justify-center rounded-lg transition-colors hover:bg-[var(--token-surface-tertiary)] md:hidden"
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
              {headerTitle && (
                <h1
                  className="text-sm font-medium truncate px-4"
                  style={{ color: 'var(--token-text-primary)' }}
                >
                  {headerTitle}
                </h1>
              )}
            </div>

            {/* Right: Actions */}
            <div className="flex items-center gap-2">
              {headerContent}
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 flex flex-col min-h-0">
            {children}
          </main>
        </div>
      </div>
    </div>
  )
}
