import { useState } from 'react'
import { Provider } from '@/types'

interface ProviderListProps {
  providers: Provider[]
  onEdit: (provider: Provider) => void
  onDelete: (id: string) => void
  onTest: (id: string) => Promise<{ success: boolean; message: string }>
}

export function ProviderList({
  providers,
  onEdit,
  onDelete,
  onTest,
}: ProviderListProps) {
  const [testingId, setTestingId] = useState<string | null>(null)
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({})

  const handleTest = async (id: string) => {
    setTestingId(id)
    try {
      const result = await onTest(id)
      setTestResults(prev => ({ ...prev, [id]: result }))
    } catch {
      setTestResults(prev => ({
        ...prev,
        [id]: { success: false, message: '连接测试失败' }
      }))
    } finally {
      setTestingId(null)
    }
  }

  const getProviderTypeLabel = (type: string) => {
    switch (type) {
      case 'llama_cpp': return 'Llama.cpp'
      case 'openai': return 'OpenAI'
      case 'custom': return '自定义'
      default: return type
    }
  }

  const getProviderTypeIcon = (type: string, isActive: boolean) => {
    const color = isActive ? '#0ea5e9' : '#94a3b8'
    switch (type) {
      case 'llama_cpp':
        return (
          <svg className="w-5 h-5" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
          </svg>
        )
      case 'openai':
        return (
          <svg className="w-5 h-5" style={{ color }} viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.981 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .743 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.26 24a6.056 6.056 0 0 0 5.772-4.206 5.99 5.99 0 0 0 3.997-2.9 6.056 6.056 0 0 0-.747-7.073zM13.26 22.43a4.476 4.476 0 0 1-2.876-1.04l.141-.081 4.779-2.758a.795.795 0 0 0 .392-.681v-6.737l2.02 1.168a.071.071 0 0 1 .038.052v5.583a4.504 4.504 0 0 1-4.494 4.494zM3.6 18.304a4.47 4.47 0 0 1-.535-3.014l.142.085 4.783 2.759a.771.771 0 0 0 .78 0l5.843-3.369v2.332a.08.08 0 0 1-.033.062L9.74 19.95a4.5 4.5 0 0 1-6.14-1.646zM2.34 7.896a4.485 4.485 0 0 1 2.366-1.973V11.6a.766.766 0 0 0 .388.676l5.815 3.355-2.02 1.168a.076.076 0 0 1-.071 0l-4.83-2.786A4.504 4.504 0 0 1 2.34 7.872zm16.597 3.855l-5.833-3.387L15.119 7.2a.076.076 0 0 1 .071 0l4.83 2.791a4.494 4.494 0 0 1-.676 8.105v-5.678a.79.79 0 0 0-.407-.667zm2.01-3.023l-.141-.085-4.774-2.782a.776.776 0 0 0-.785 0L9.409 9.23V6.897a.066.066 0 0 1 .028-.061l4.83-2.787a4.5 4.5 0 0 1 6.68 4.66zm-12.64 4.135l-2.02-1.164a.08.08 0 0 1-.038-.057V6.075a4.5 4.5 0 0 1 7.375-3.453l-.142.08L8.704 5.46a.795.795 0 0 0-.393.681zm1.097-2.365l2.602-1.5 2.607 1.5v2.999l-2.597 1.5-2.607-1.5z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
          </svg>
        )
    }
  }

  if (providers.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '2.5rem 1rem' }}>
        <div
          style={{
            width: '3.5rem',
            height: '3.5rem',
            margin: '0 auto 1rem',
            borderRadius: '1rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.03))',
          }}
        >
          <svg
            style={{ width: '1.75rem', height: '1.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
          </svg>
        </div>
        <p style={{ color: 'var(--token-text-primary, #0d0d0d)', fontSize: '0.875rem', fontWeight: 500 }}>
          尚未配置提供商
        </p>
        <p style={{ color: 'var(--token-text-tertiary, #8f8f8f)', fontSize: '0.75rem', marginTop: '0.25rem' }}>
          添加一个提供商以开始使用
        </p>
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      {providers.map(provider => {
        const testResult = testResults[provider.id]
        return (
          <div
            key={provider.id}
            style={{
              borderRadius: '1rem',
              padding: '1rem',
              transition: 'all 0.2s ease',
              background: 'var(--token-main-surface-primary, #fff)',
              border: `1px solid ${provider.is_active ? 'var(--token-border-default, rgba(0, 0, 0, 0.1))' : 'var(--token-border-light, rgba(0, 0, 0, 0.05))'}`,
              boxShadow: '0 1px 2px rgba(0, 0, 0, 0.04)',
              opacity: provider.is_active ? 1 : 0.6,
              cursor: 'default',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.08)'
              e.currentTarget.style.transform = 'translateY(-1px)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 1px 2px rgba(0, 0, 0, 0.04)'
              e.currentTarget.style.transform = 'translateY(0)'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.875rem' }}>
                {/* Icon */}
                <div
                  style={{
                    width: '2.5rem',
                    height: '2.5rem',
                    borderRadius: '0.75rem',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: provider.is_active
                      ? 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))'
                      : 'var(--token-surface-tertiary, rgba(0, 0, 0, 0.03))',
                    transition: 'background 0.2s',
                  }}
                >
                  {getProviderTypeIcon(provider.provider_type, provider.is_active)}
                </div>

                {/* Info */}
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
                    <h4 style={{ fontWeight: 500, color: 'var(--token-text-primary, #0d0d0d)', fontSize: '0.9375rem' }}>
                      {provider.name}
                    </h4>
                    <span
                      style={{
                        padding: '0.125rem 0.5rem',
                        borderRadius: '9999px',
                        fontSize: '0.75rem',
                        fontWeight: 500,
                        background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))',
                        color: 'var(--token-text-secondary, #5d5d5d)',
                      }}
                    >
                      {getProviderTypeLabel(provider.provider_type)}
                    </span>
                    {!provider.is_active && (
                      <span
                        style={{
                          padding: '0.125rem 0.5rem',
                          borderRadius: '9999px',
                          fontSize: '0.75rem',
                          fontWeight: 500,
                          background: 'rgba(245, 158, 11, 0.1)',
                          color: '#d97706',
                        }}
                      >
                        未启用
                      </span>
                    )}
                  </div>
                  {provider.base_url && (
                    <p style={{
                      fontSize: '0.75rem',
                      color: 'var(--token-text-tertiary, #8f8f8f)',
                      fontFamily: 'var(--font-mono, ui-monospace, monospace)',
                      marginTop: '0.25rem',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                    }}>
                      {provider.base_url}
                    </p>
                  )}
                  {(() => {
                    const model = provider.config?.default_model
                    if (model && typeof model === 'string') {
                      return (
                        <p style={{ fontSize: '0.75rem', color: 'var(--token-text-accent, #3a83f7)', marginTop: '0.25rem' }}>
                          模型：<span style={{ fontFamily: 'var(--font-mono, ui-monospace, monospace)' }}>{model}</span>
                        </p>
                      )
                    }
                    return null
                  })()}
                </div>
              </div>

              {/* Actions */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                <button
                  onClick={() => handleTest(provider.id)}
                  disabled={testingId === provider.id}
                  style={{
                    padding: '0.5rem',
                    borderRadius: '0.5rem',
                    color: 'var(--token-text-tertiary, #8f8f8f)',
                    background: 'transparent',
                    border: 'none',
                    cursor: testingId === provider.id ? 'default' : 'pointer',
                    opacity: testingId === provider.id ? 0.5 : 1,
                    transition: 'all 0.15s',
                  }}
                  onMouseEnter={(e) => {
                    if (testingId !== provider.id) {
                      e.currentTarget.style.color = 'var(--token-text-accent, #3a83f7)'
                      e.currentTarget.style.background = 'var(--token-surface-hover, rgba(0, 0, 0, 0.04))'
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--token-text-tertiary, #8f8f8f)'
                    e.currentTarget.style.background = 'transparent'
                  }}
                  title="测试连接"
                >
                  {testingId === provider.id ? (
                    <div
                      style={{
                        width: '1.25rem',
                        height: '1.25rem',
                        borderRadius: '50%',
                        border: '2px solid var(--token-text-accent, #3a83f7)',
                        borderTopColor: 'transparent',
                        animation: 'spin 1s linear infinite',
                      }}
                    />
                  ) : (
                    <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  )}
                </button>
                <button
                  onClick={() => onEdit(provider)}
                  style={{
                    padding: '0.5rem',
                    borderRadius: '0.5rem',
                    color: 'var(--token-text-tertiary, #8f8f8f)',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--token-text-secondary, #5d5d5d)'
                    e.currentTarget.style.background = 'var(--token-surface-hover, rgba(0, 0, 0, 0.04))'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--token-text-tertiary, #8f8f8f)'
                    e.currentTarget.style.background = 'transparent'
                  }}
                  title="编辑提供商"
                >
                  <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button
                  onClick={() => onDelete(provider.id)}
                  style={{
                    padding: '0.5rem',
                    borderRadius: '0.5rem',
                    color: 'var(--token-text-tertiary, #8f8f8f)',
                    background: 'transparent',
                    border: 'none',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.color = 'var(--token-text-status-error, #ef4444)'
                    e.currentTarget.style.background = 'rgba(239, 68, 68, 0.08)'
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.color = 'var(--token-text-tertiary, #8f8f8f)'
                    e.currentTarget.style.background = 'transparent'
                  }}
                  title="删除提供商"
                >
                  <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Test Result */}
            {testResult && (
              <div
                style={{
                  marginTop: '0.75rem',
                  padding: '0.625rem 0.875rem',
                  borderRadius: '0.5rem',
                  fontSize: '0.8125rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  background: testResult.success
                    ? 'rgba(16, 185, 129, 0.06)'
                    : 'rgba(239, 68, 68, 0.06)',
                  color: testResult.success ? '#059669' : '#dc2626',
                }}
              >
                {testResult.success ? (
                  <svg style={{ width: '1rem', height: '1rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg style={{ width: '1rem', height: '1rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                <span>{testResult.message}</span>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
