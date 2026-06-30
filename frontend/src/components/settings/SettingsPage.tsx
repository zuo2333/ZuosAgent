import { useState, useEffect } from 'react'
import { Provider, GlobalConfig, CreateProviderData } from '@/types'
import { ProviderForm, ProviderList, GlobalConfigPanel } from '@/components/config'
import { ConfirmDialog } from '@/components/ui'

interface SettingsPageProps {
  providers: Provider[]
  globalConfig: GlobalConfig | null
  isLoading: boolean
  onCreateProvider: (data: CreateProviderData) => Promise<Provider>
  onUpdateProvider: (id: string, data: Partial<Provider>) => Promise<Provider>
  onDeleteProvider: (id: string) => Promise<void>
  onTestProvider: (id: string) => Promise<{ success: boolean; message: string }>
  onUpdateGlobalConfig: (data: Partial<GlobalConfig>) => Promise<void>
  onClose?: () => void
}

type SettingsTab = 'providers' | 'defaults'

export function SettingsPage({
  providers,
  globalConfig,
  isLoading,
  onCreateProvider,
  onUpdateProvider,
  onDeleteProvider,
  onTestProvider,
  onUpdateGlobalConfig,
  onClose,
}: SettingsPageProps) {
  const [activeTab, setActiveTab] = useState<SettingsTab>('providers')
  const [showProviderForm, setShowProviderForm] = useState(false)
  const [editingProvider, setEditingProvider] = useState<Provider | null>(null)
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; name: string } | null>(null)
  const [isSaving, setIsSaving] = useState(false)

  // Close form when tab changes
  useEffect(() => {
    setShowProviderForm(false)
    setEditingProvider(null)
  }, [activeTab])

  const handleCreateProvider = async (data: CreateProviderData) => {
    setIsSaving(true)
    try {
      await onCreateProvider(data)
      setShowProviderForm(false)
    } catch (error) {
      console.error('Failed to create provider:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleUpdateProvider = async (data: CreateProviderData) => {
    if (!editingProvider) return
    setIsSaving(true)
    try {
      await onUpdateProvider(editingProvider.id, data)
      setEditingProvider(null)
    } catch (error) {
      console.error('Failed to update provider:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteProvider = async () => {
    if (!deleteConfirm) return
    try {
      await onDeleteProvider(deleteConfirm.id)
      setDeleteConfirm(null)
    } catch (error) {
      console.error('Failed to delete provider:', error)
    }
  }

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    {
      id: 'providers',
      label: '模型提供商',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
        </svg>
      ),
    },
    {
      id: 'defaults',
      label: '默认设置',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      ),
    },
  ]

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center p-4 animate-fade-in">
      {/* Backdrop */}
      <div
        className="absolute inset-0"
        style={{
          background: 'rgba(15, 23, 42, 0.3)',
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
        }}
        onClick={onClose}
      />

      {/* Modal - ChatGPT style settings dialog */}
      <div
        role="dialog"
        aria-modal="true"
        data-state="open"
        className="relative w-full flex flex-col md:flex-row overflow-hidden rounded-2xl"
        style={{
          background: 'var(--token-main-surface-primary)',
          maxWidth: '680px',
          height: '420px',
          maxHeight: '85vh',
          boxShadow: '0px 8px 12px 0px rgba(0, 0, 0, 0.08), 0px 0px 1px 0px rgba(0, 0, 0, 0.62)',
        }}
      >
        {/* Left Sidebar - Navigation */}
        <div
          role="tablist"
          aria-orientation="vertical"
          className="flex flex-row md:flex-col shrink-0 border-b md:border-b-0 md:border-e overflow-x-auto md:overflow-visible"
          style={{
            width: 'auto',
            minWidth: 'auto',
            borderColor: 'var(--token-border-light)',
            padding: '0.75rem',
            gap: '0.25rem',
          }}
        >
          {/* Close button - desktop only */}
          {onClose && (
            <button
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-lg transition-colors mb-2"
              style={{
                color: 'var(--token-text-secondary)',
                background: 'transparent',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              aria-label="Close"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}

          {/* Mobile gradient mask for scroll hint */}
          <div
            className="md:hidden shrink-0 sticky end-0 z-10 min-w-2"
            style={{
              background: 'linear-gradient(to left, var(--token-main-surface-primary), transparent)',
            }}
          />

          {/* Tab buttons */}
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                role="tab"
                aria-selected={isActive}
                data-state={isActive ? 'active' : 'inactive'}
                aria-controls={`tabpanel-${tab.id}`}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2 rounded-lg transition-colors whitespace-nowrap"
                style={{
                  background: isActive ? 'var(--token-surface-tertiary)' : 'transparent',
                  color: 'var(--token-text-primary)',
                  padding: '0.625rem 0.75rem',
                }}
                onMouseEnter={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'var(--token-surface-hover)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isActive) {
                    e.currentTarget.style.background = 'transparent'
                  }
                }}
              >
                <span className="flex items-center justify-center" style={{ opacity: 1 }}>
                  {tab.icon}
                </span>
                <span className="flex min-w-0 grow items-center">
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>{tab.label}</span>
                </span>
              </button>
            )
          })}
        </div>

        {/* Right Content Area */}
        <div
          role="tabpanel"
          id={`tabpanel-${activeTab}`}
          aria-labelledby={activeTab}
          className="flex-1 flex flex-col overflow-y-auto"
          style={{
            background: 'var(--token-main-surface-primary)',
          }}
        >
          {/* Section Header - 与内容区域对齐 */}
          <div
            style={{
              padding: '1.25rem 1.25rem 1rem',
              borderBottom: '1px solid var(--token-border-light, rgba(0, 0, 0, 0.05))',
            }}
          >
            <h2 style={{
              fontSize: '1rem',
              fontWeight: 600,
              color: 'var(--token-text-primary, #0d0d0d)',
              lineHeight: 1.5,
            }}>
              {activeTab === 'providers' ? '模型提供商' : '默认设置'}
            </h2>
          </div>

          {/* Close button - mobile only */}
          {onClose && (
            <div className="md:hidden flex justify-end p-2 border-b" style={{ borderColor: 'var(--token-border-light)' }}>
              <button
                onClick={onClose}
                className="flex h-9 w-9 items-center justify-center rounded-lg transition-colors"
                style={{
                  color: 'var(--token-text-secondary)',
                  background: 'transparent',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                aria-label="Close"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}

          {/* Content - 宽松的内边距创造呼吸感，与标题对齐 */}
          <div className="flex-1 overflow-y-auto" style={{ padding: '0 1.25rem 1.25rem' }}>
            <div style={{ paddingTop: '1rem' }}>
            {activeTab === 'providers' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {/* Add Provider Button */}
                {!showProviderForm && !editingProvider && (
                  <button
                    onClick={() => setShowProviderForm(true)}
                    className="w-full flex items-center justify-center gap-2 transition-colors"
                    style={{
                      background: 'transparent',
                      border: '1px dashed var(--token-border-heavy, rgba(0, 0, 0, 0.15))',
                      borderRadius: '1rem',
                      padding: '1rem',
                      color: 'var(--token-text-primary)',
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'var(--token-surface-hover, rgba(0, 0, 0, 0.03))'
                      e.currentTarget.style.borderColor = 'var(--token-border-medium, rgba(0, 0, 0, 0.25))'
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = 'transparent'
                      e.currentTarget.style.borderColor = 'var(--token-border-heavy, rgba(0, 0, 0, 0.15))'
                    }}
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
                    </svg>
                    <span style={{ fontWeight: 500 }}>添加提供商</span>
                  </button>
                )}

                {/* Provider Form */}
                {(showProviderForm || editingProvider) && (
                  <div className="flex justify-center">
                    <ProviderForm
                      provider={editingProvider || undefined}
                      onSave={editingProvider ? handleUpdateProvider : handleCreateProvider}
                      onTest={onTestProvider}
                      onCancel={() => {
                        setShowProviderForm(false)
                        setEditingProvider(null)
                      }}
                      isSaving={isSaving}
                    />
                  </div>
                )}

                {/* Provider List */}
                {!showProviderForm && !editingProvider && (
                  <ProviderList
                    providers={providers}
                    onEdit={setEditingProvider}
                    onDelete={(id) => {
                      const provider = providers.find(p => p.id === id)
                      if (provider) {
                        setDeleteConfirm({ id, name: provider.name })
                      }
                    }}
                    onTest={onTestProvider}
                  />
                )}
              </div>
            )}

            {activeTab === 'defaults' && (
              <GlobalConfigPanel
                config={globalConfig}
                providers={providers}
                onUpdateConfig={onUpdateGlobalConfig}
                isLoading={isLoading}
              />
            )}
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="删除提供商"
        message={`确定要删除 "${deleteConfirm?.name}" 吗？此操作无法撤销。`}
        confirmText="删除"
        confirmVariant="danger"
        onConfirm={handleDeleteProvider}
        onCancel={() => setDeleteConfirm(null)}
      />
    </div>
  )
}
