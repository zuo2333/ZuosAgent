import { useEffect, useCallback, useState, useRef } from 'react'
import { AppLayout } from '@/components/layout'
import { ChatPanel } from '@/components/chat'
import { SessionList, SessionSettings } from '@/components/session'
import { SettingsPage } from '@/components/settings'
import { ConfirmDialog } from '@/components/ui'
import { useSessionStore } from '@/stores/sessionStore'
import { useConfigStore } from '@/stores/configStore'

function App() {
  const {
    sessions,
    currentSession,
    messages,
    isLoading: sessionLoading,
    error,
    fetchSessions,
    createSession,
    deleteSession,
    updateSession,
    setCurrentSession,
    setMessages,
    clearError,
  } = useSessionStore()

  const {
    providers,
    globalConfig,
    isLoading: configLoading,
    fetchProviders,
    createProvider,
    updateProvider,
    deleteProvider,
    testProviderConnection,
    fetchGlobalConfig,
    updateGlobalConfig,
  } = useConfigStore()

  // UI State
  const [showSettings, setShowSettings] = useState(false)
  const [showSessionSettings, setShowSessionSettings] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; title: string } | null>(null)
  const sessionSettingsTriggerRef = useRef<HTMLButtonElement>(null)

  // Fetch initial data
  useEffect(() => {
    fetchSessions()
    fetchProviders()
    fetchGlobalConfig()
  }, [fetchSessions, fetchProviders, fetchGlobalConfig])

  // Session handlers
  const handleCreateSession = useCallback(async () => {
    try {
      const session = await createSession({ title: '新对话' })
      return session?.id
    } catch (err) {
      console.error('Failed to create session:', err)
      return undefined
    }
  }, [createSession])

  const handleDeleteSession = useCallback(async (id: string) => {
    try {
      await deleteSession(id)
      setDeleteConfirm(null)
    } catch (err) {
      console.error('Failed to delete session:', err)
    }
  }, [deleteSession])

  const handleRenameSession = useCallback(async (id: string, title: string) => {
    try {
      await updateSession(id, { title })
    } catch (err) {
      console.error('Failed to rename session:', err)
    }
  }, [updateSession])

  const handleMessagesUpdate = useCallback((newMessages: typeof messages) => {
    setMessages(newMessages)
  }, [setMessages])

  const handleTitleGenerated = useCallback(async (sessionId: string, title: string) => {
    try {
      await updateSession(sessionId, { title })
    } catch (err) {
      console.error('Failed to update session title:', err)
    }
  }, [updateSession])

  // Provider handlers
  const handleCreateProvider = useCallback(async (data: Parameters<typeof createProvider>[0]) => {
    return createProvider(data)
  }, [createProvider])

  const handleUpdateProvider = useCallback(async (id: string, data: Parameters<typeof updateProvider>[1]) => {
    return updateProvider(id, data)
  }, [updateProvider])

  const handleDeleteProvider = useCallback(async (id: string) => {
    return deleteProvider(id)
  }, [deleteProvider])

  const handleTestProvider = useCallback(async (id: string) => {
    return testProviderConnection(id)
  }, [testProviderConnection])

  // Global config handler
  const handleUpdateGlobalConfig = useCallback(async (data: Parameters<typeof updateGlobalConfig>[0]) => {
    return updateGlobalConfig(data)
  }, [updateGlobalConfig])

  return (
    <>
      <AppLayout
        headerTitle={currentSession?.title}
        headerContent={
          currentSession && (
            <div style={{ position: 'relative' }}>
              <button
                ref={sessionSettingsTriggerRef}
                onClick={() => setShowSessionSettings(!showSessionSettings)}
                className="flex items-center justify-center rounded-lg transition-colors"
                style={{
                  width: '36px',
                  height: '36px',
                  background: showSessionSettings ? 'var(--token-surface-tertiary)' : 'transparent',
                  color: showSessionSettings ? 'var(--token-text-primary)' : 'var(--token-text-tertiary)',
                }}
                title="Session settings"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                </svg>
              </button>
              {/* Session Settings Popover */}
              {showSessionSettings && (
                <SessionSettings
                  session={currentSession}
                  providers={providers}
                  onUpdateSession={updateSession}
                  onClose={() => setShowSessionSettings(false)}
                  triggerRef={sessionSettingsTriggerRef}
                />
              )}
            </div>
          )
        }
        sidebarContent={
          <SessionList
            sessions={sessions}
            currentSession={currentSession}
            isLoading={sessionLoading}
            onSelectSession={setCurrentSession}
            onCreateSession={handleCreateSession}
            onDeleteSession={(id) => {
              const session = sessions.find(s => s.id === id)
              if (session) {
                setDeleteConfirm({ id, title: session.title || 'Untitled' })
              }
            }}
            onRenameSession={handleRenameSession}
          />
        }
        sidebarBottomContent={
          <button
            onClick={() => setShowSettings(true)}
            className="__menu-item hoverable gap-2"
          >
            <span className="icon flex items-center justify-center w-6 h-6">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </span>
            <span className="text-sm">设置</span>
          </button>
        }
      >
        {/* Main Content */}
        <div className="flex flex-1 min-h-0">
          {/* Chat Panel */}
          <div className="flex-1 flex flex-col min-w-0">
            <ChatPanel
              sessionId={currentSession?.id || null}
              messages={messages}
              onMessagesUpdate={handleMessagesUpdate}
              onTitleGenerated={handleTitleGenerated}
              onCreateSession={handleCreateSession}
            />
          </div>
        </div>
      </AppLayout>

      {/* Settings Modal */}
      {showSettings && (
        <SettingsPage
          providers={providers}
          globalConfig={globalConfig}
          isLoading={configLoading}
          onCreateProvider={handleCreateProvider}
          onUpdateProvider={handleUpdateProvider}
          onDeleteProvider={handleDeleteProvider}
          onTestProvider={handleTestProvider}
          onUpdateGlobalConfig={handleUpdateGlobalConfig}
          onClose={() => setShowSettings(false)}
        />
      )}

      {/* Delete Session Confirmation Dialog */}
      <ConfirmDialog
        isOpen={!!deleteConfirm}
        title="删除对话"
        message={`确定要删除 "${deleteConfirm?.title}" 吗？此操作无法撤销。`}
        confirmText="删除"
        confirmVariant="danger"
        onConfirm={() => deleteConfirm && handleDeleteSession(deleteConfirm.id)}
        onCancel={() => setDeleteConfirm(null)}
      />

      {/* Error Toast */}
      {error && (
        <div
          className="fixed bottom-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg flex items-center gap-2"
          style={{
            background: 'var(--color-error)',
            color: 'white',
          }}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm">{error}</span>
          <button
            onClick={clearError}
            className="ml-2 opacity-70 hover:opacity-100"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}
    </>
  )
}

export default App
