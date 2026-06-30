import { useState, useEffect, useRef, RefObject } from 'react'
import { Session, Provider } from '@/types'
import { ToolSettings } from '@/components/chat'
import { useOnClickOutside } from '@/hooks'

interface SessionSettingsProps {
  session: Session
  providers: Provider[]
  onUpdateSession: (id: string, data: Partial<Session>) => Promise<void>
  onClose?: () => void
  triggerRef?: RefObject<HTMLButtonElement | null>
}

export function SessionSettings({
  session,
  providers,
  onUpdateSession,
  onClose,
  triggerRef,
}: SessionSettingsProps) {
  const [temperature, setTemperature] = useState(session.temperature ?? 0.7)
  const [maxTokens, setMaxTokens] = useState(session.max_tokens ?? 2048)
  const [systemPrompt, setSystemPrompt] = useState(session.system_prompt ?? '')
  const [selectedProvider, setSelectedProvider] = useState(session.provider_id ?? '')
  const [selectedModel, setSelectedModel] = useState(session.model ?? '')
  const [toolsEnabled, setToolsEnabled] = useState<string[]>(session.enabled_tools ?? [])
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)
  const [showConfirmClose, setShowConfirmClose] = useState(false)

  const panelRef = useRef<HTMLDivElement>(null)

  // Click outside to close (only if no unsaved changes)
  useOnClickOutside(panelRef, (e) => {
    // Don't close if clicking the trigger button (it handles its own toggle)
    if (triggerRef?.current?.contains(e.target as Node)) {
      return
    }

    if (hasChanges) {
      setShowConfirmClose(true)
    } else {
      onClose?.()
    }
  }, true)

  // Get available models for selected provider
  const selectedProviderData = providers.find(p => p.id === selectedProvider)
  const availableModels = selectedProviderData?.config?.models as string[] || []

  // Check for changes
  useEffect(() => {
    const changed =
      temperature !== (session.temperature ?? 0.7) ||
      maxTokens !== (session.max_tokens ?? 2048) ||
      systemPrompt !== (session.system_prompt ?? '') ||
      selectedProvider !== (session.provider_id ?? '') ||
      selectedModel !== (session.model ?? '') ||
      JSON.stringify(toolsEnabled.sort()) !== JSON.stringify((session.enabled_tools ?? []).sort())
    setHasChanges(changed)
  }, [temperature, maxTokens, systemPrompt, selectedProvider, selectedModel, toolsEnabled, session])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onUpdateSession(session.id, {
        temperature,
        max_tokens: maxTokens,
        system_prompt: systemPrompt || null,
        provider_id: selectedProvider || null,
        model: selectedModel || null,
        enabled_tools: toolsEnabled,
      })
      setHasChanges(false)
    } catch (error) {
      console.error('Failed to save session settings:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleToolsChange = (tools: string[]) => {
    setToolsEnabled(tools)
  }

  const handleConfirmClose = () => {
    setShowConfirmClose(false)
    onClose?.()
  }

  const handleCancelClose = () => {
    setShowConfirmClose(false)
  }

  const handleReset = () => {
    setTemperature(session.temperature ?? 0.7)
    setMaxTokens(session.max_tokens ?? 2048)
    setSystemPrompt(session.system_prompt ?? '')
    setSelectedProvider(session.provider_id ?? '')
    setSelectedModel(session.model ?? '')
    setToolsEnabled(session.enabled_tools ?? [])
  }

  return (
    <div
      ref={panelRef}
      className="rounded-2xl overflow-hidden"
      style={{
        position: 'absolute',
        top: '48px',
        right: '0',
        width: 'min(400px, calc(100vw - 32px))',
        maxHeight: 'min(500px, calc(100vh - 80px))',
        background: 'var(--token-main-surface-primary)',
        border: '1px solid var(--token-border-light)',
        boxShadow: '0px 8px 12px 0px rgba(0, 0, 0, 0.08), 0px 0px 1px 0px rgba(0, 0, 0, 0.62)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 50,
      }}
    >
      {/* Header - matches SettingsPage Section Header style */}
      <div
        style={{
          padding: '1.25rem 1.25rem 1rem',
          borderBottom: '1px solid var(--token-border-light)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <h2 style={{
          fontSize: '1rem',
          fontWeight: 600,
          color: 'var(--token-text-primary)',
          lineHeight: 1.5,
        }}>
          会话设置
        </h2>
        {onClose && (
          <button
            onClick={() => {
              if (hasChanges) {
                setShowConfirmClose(true)
              } else {
                onClose()
              }
            }}
            className="rounded-lg w-8 h-8 flex items-center justify-center motion-safe:transition-colors"
            style={{ color: 'var(--token-text-tertiary)' }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Content - scrollable */}
      <div className="flex-1 overflow-y-auto" style={{ padding: '1rem 1.25rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {/* Model Provider Selection */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="text-sm font-medium" style={{ color: 'var(--token-text-primary)' }}>模型提供商</label>
            <select
              value={selectedProvider}
              onChange={(e) => {
                setSelectedProvider(e.target.value)
                setSelectedModel('')
              }}
              className="w-full py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{
                background: 'var(--token-surface-secondary)',
                border: '1px solid var(--token-border-light)',
                color: 'var(--token-text-primary)',
                padding: '0.625rem 0.875rem',
              }}
            >
              <option value="">使用默认</option>
              {providers.map(provider => (
                <option key={provider.id} value={provider.id}>
                  {provider.name} ({provider.provider_type})
                </option>
              ))}
            </select>
          </div>

          {selectedProvider && availableModels.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <label className="text-sm font-medium" style={{ color: 'var(--token-text-primary)' }}>模型</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2"
                style={{
                  background: 'var(--token-surface-secondary)',
                  border: '1px solid var(--token-border-light)',
                  color: 'var(--token-text-primary)',
                  padding: '0.625rem 0.875rem',
                }}
              >
                <option value="">选择模型</option>
                {availableModels.map(model => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Divider */}
          <div style={{ height: '1px', background: 'var(--token-border-light)' }} />

          {/* Temperature Slider */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <label className="text-sm font-medium" style={{ color: 'var(--token-text-primary)' }}>温度</label>
              <span
                className="text-sm px-2 py-0.5 rounded"
                style={{
                  color: 'var(--token-text-secondary)',
                  background: 'var(--token-surface-tertiary)',
                }}
              >
                {temperature.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min="0"
              max="2"
              step="0.01"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full h-2 rounded-lg appearance-none cursor-pointer"
              style={{ background: 'var(--token-surface-tertiary)' }}
            />
            <div className="flex justify-between text-xs" style={{ color: 'var(--token-text-tertiary)' }}>
              <span>精确 (0)</span>
              <span>创意 (2)</span>
            </div>
          </div>

          {/* Max Tokens */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="text-sm font-medium" style={{ color: 'var(--token-text-primary)' }}>最大 Token</label>
            <input
              type="number"
              min="1"
              max="128000"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value) || 2048)}
              className="w-full py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2"
              style={{
                background: 'var(--token-surface-secondary)',
                border: '1px solid var(--token-border-light)',
                color: 'var(--token-text-primary)',
                padding: '0.625rem 0.875rem',
              }}
            />
          </div>

          {/* System Prompt */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label className="text-sm font-medium" style={{ color: 'var(--token-text-primary)' }}>系统提示词</label>
            <textarea
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="输入自定义系统提示词..."
              rows={3}
              className="w-full py-2.5 rounded-lg text-sm focus:outline-none focus:ring-2 resize-none font-mono"
              style={{
                background: 'var(--token-surface-secondary)',
                border: '1px solid var(--token-border-light)',
                color: 'var(--token-text-primary)',
                padding: '0.625rem 0.875rem',
              }}
            />
          </div>

          {/* Divider */}
          <div style={{ height: '1px', background: 'var(--token-border-light)' }} />

          {/* Tools */}
          <ToolSettings
            enabledTools={toolsEnabled}
            onToolsChange={handleToolsChange}
          />
        </div>
      </div>

      {/* Footer */}
      {hasChanges && (
        <div
          style={{
            padding: '1rem 1.25rem',
            borderTop: '1px solid var(--token-border-light)',
            background: 'var(--token-surface-secondary)',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '0.75rem',
          }}
        >
          <button
            onClick={handleReset}
            className="px-4 py-2 text-sm font-medium rounded-lg motion-safe:transition-colors"
            style={{ color: 'var(--token-text-secondary)' }}
            onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover)'}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            重置
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="px-4 py-2 text-sm font-medium rounded-lg motion-safe:transition-colors"
            style={{
              background: 'var(--token-text-primary)',
              color: 'var(--token-surface-primary)',
            }}
          >
            {isSaving ? '保存中...' : '保存更改'}
          </button>
        </div>
      )}

      {/* Confirm Close Dialog */}
      {showConfirmClose && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10,
          }}
        >
          <div
            className="rounded-xl"
            style={{
              background: 'var(--token-main-surface-primary)',
              padding: '1.25rem',
              maxWidth: '280px',
              boxShadow: '0px 8px 12px 0px rgba(0, 0, 0, 0.08)',
            }}
          >
            <h3 className="text-sm font-semibold mb-2" style={{ color: 'var(--token-text-primary)' }}>
              有未保存的更改
            </h3>
            <p className="text-sm mb-4" style={{ color: 'var(--token-text-secondary)' }}>
              确定要关闭吗？未保存的更改将丢失。
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button
                onClick={handleCancelClose}
                className="px-3 py-1.5 text-sm rounded-lg"
                style={{ color: 'var(--token-text-secondary)' }}
              >
                取消
              </button>
              <button
                onClick={handleConfirmClose}
                className="px-3 py-1.5 text-sm rounded-lg"
                style={{
                  background: 'var(--color-error, #ef4444)',
                  color: 'white',
                }}
              >
                放弃更改
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
