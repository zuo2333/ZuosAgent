import { useEffect, useRef } from 'react'

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmVariant?: 'danger' | 'primary'
  onConfirm: () => void
  onCancel: () => void
}

export function ConfirmDialog({
  isOpen,
  title,
  message,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmVariant = 'danger',
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const confirmButtonRef = useRef<HTMLButtonElement>(null)

  // Focus trap and escape key handling
  useEffect(() => {
    if (isOpen) {
      // Focus the confirm button when dialog opens
      confirmButtonRef.current?.focus()

      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onCancel()
        }
      }

      document.addEventListener('keydown', handleEscape)

      // Prevent body scroll
      document.body.style.overflow = 'hidden'

      return () => {
        document.removeEventListener('keydown', handleEscape)
        document.body.style.overflow = ''
      }
    }
  }, [isOpen, onCancel])

  if (!isOpen) return null

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onCancel()
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center animate-fade-in"
      style={{
        background: 'rgba(15, 23, 42, 0.3)',
        backdropFilter: 'blur(8px)',
        WebkitBackdropFilter: 'blur(8px)',
      }}
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="dialog-title"
    >
      <div
        ref={dialogRef}
        className="relative flex flex-col overflow-hidden"
        style={{
          background: 'var(--token-main-surface-primary)',
          borderRadius: 'var(--radius-2xl)',
          boxShadow: '0px 8px 12px 0px rgba(0, 0, 0, 0.08), 0px 0px 1px 0px rgba(0, 0, 0, 0.62)',
          width: '100%',
          maxWidth: '456px',
          margin: '0 24px',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '1.25rem 1.25rem 0',
          }}
        >
          <h2
            id="dialog-title"
            style={{
              fontSize: '1rem',
              fontWeight: 600,
              color: 'var(--token-text-primary)',
              lineHeight: 1.5,
            }}
          >
            {title}
          </h2>
        </div>

        {/* Content */}
        <div style={{ padding: '0.5rem 1.25rem 1.25rem' }}>
          <p
            style={{
              fontSize: '0.875rem',
              color: 'var(--token-text-secondary)',
              lineHeight: 1.5,
            }}
          >
            {message}
          </p>
        </div>

        {/* Actions */}
        <div
          className="flex justify-end gap-2"
          style={{
            padding: '0.75rem 1rem',
            borderTop: '1px solid var(--token-border-light)',
          }}
        >
          <button
            onClick={onCancel}
            className="flex items-center justify-center rounded-lg transition-colors"
            style={{
              padding: '0.5rem 1rem',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: 'var(--token-text-primary)',
              background: 'transparent',
              minWidth: '64px',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            {cancelText}
          </button>
          <button
            ref={confirmButtonRef}
            onClick={onConfirm}
            className="flex items-center justify-center rounded-lg transition-colors"
            style={{
              padding: '0.5rem 1rem',
              fontSize: '0.875rem',
              fontWeight: 500,
              color: confirmVariant === 'danger' ? '#ef4444' : 'var(--token-text-primary)',
              background: 'var(--token-surface-tertiary)',
              minWidth: '64px',
            }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'var(--token-surface-tertiary)'}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}
