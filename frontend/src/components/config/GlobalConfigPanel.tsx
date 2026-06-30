import { useState, useEffect } from 'react'
import { GlobalConfig, Provider } from '@/types'

interface GlobalConfigPanelProps {
  config: GlobalConfig | null
  providers: Provider[]
  onUpdateConfig: (data: Partial<GlobalConfig>) => Promise<void>
  isLoading?: boolean
}

export function GlobalConfigPanel({
  config,
  providers,
  onUpdateConfig,
  isLoading = false,
}: GlobalConfigPanelProps) {
  const [defaultProvider, setDefaultProvider] = useState('')
  const [defaultModel, setDefaultModel] = useState('')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(2048)
  const [systemPrompt, setSystemPrompt] = useState('')
  const [allowedTables, setAllowedTables] = useState<string[]>([])
  const [newTable, setNewTable] = useState('')
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  // Get available models for selected provider
  const selectedProviderData = providers.find(p => p.id === defaultProvider)
  const availableModels = selectedProviderData?.config?.models as string[] || []

  // Initialize from config
  useEffect(() => {
    if (config) {
      setDefaultProvider(config.default_provider ?? '')
      setDefaultModel(config.default_model ?? '')
      setTemperature(config.default_temperature)
      setMaxTokens(config.default_max_tokens)
      setSystemPrompt(config.default_system_prompt)
      setAllowedTables(config.db_query_allowed_tables ?? [])
    }
  }, [config])

  // Check for changes
  useEffect(() => {
    if (config) {
      const changed =
        defaultProvider !== (config.default_provider ?? '') ||
        defaultModel !== (config.default_model ?? '') ||
        temperature !== config.default_temperature ||
        maxTokens !== config.default_max_tokens ||
        systemPrompt !== config.default_system_prompt ||
        JSON.stringify(allowedTables.sort()) !== JSON.stringify((config.db_query_allowed_tables ?? []).sort())
      setHasChanges(changed)
    }
  }, [defaultProvider, defaultModel, temperature, maxTokens, systemPrompt, allowedTables, config])

  const handleSave = async () => {
    setIsSaving(true)
    try {
      await onUpdateConfig({
        default_provider: defaultProvider || null,
        default_model: defaultModel || null,
        default_temperature: temperature,
        default_max_tokens: maxTokens,
        default_system_prompt: systemPrompt,
        db_query_allowed_tables: allowedTables,
      })
      setHasChanges(false)
    } catch (error) {
      console.error('Failed to save global config:', error)
    } finally {
      setIsSaving(false)
    }
  }

  const handleAddTable = () => {
    const table = newTable.trim()
    if (table && !allowedTables.includes(table)) {
      setAllowedTables(prev => [...prev, table])
      setNewTable('')
    }
  }

  const handleRemoveTable = (table: string) => {
    setAllowedTables(prev => prev.filter(t => t !== table))
  }

  const handleTableKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddTable()
    }
  }

  const handleReset = () => {
    if (config) {
      setDefaultProvider(config.default_provider ?? '')
      setDefaultModel(config.default_model ?? '')
      setTemperature(config.default_temperature)
      setMaxTokens(config.default_max_tokens)
      setSystemPrompt(config.default_system_prompt)
      setAllowedTables(config.db_query_allowed_tables ?? [])
    }
  }

  if (isLoading) {
    return (
      <div
        style={{
          background: 'var(--token-main-surface-primary, #fff)',
          borderRadius: '1rem',
          border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
          padding: '1.5rem',
        }}
      >
        <div style={{ animation: 'pulse 2s infinite' }}>
          <div style={{ height: '1.5rem', background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))', borderRadius: '0.5rem', width: '25%', marginBottom: '1rem' }} />
          <div style={{ height: '2.5rem', background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))', borderRadius: '0.5rem', marginBottom: '0.75rem' }} />
          <div style={{ height: '2.5rem', background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))', borderRadius: '0.5rem', marginBottom: '0.75rem' }} />
          <div style={{ height: '6rem', background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))', borderRadius: '0.5rem' }} />
        </div>
      </div>
    )
  }

  return (
    <div
      style={{
        background: 'var(--token-main-surface-primary, #fff)',
        borderRadius: '1rem',
        border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '0.875rem 1.25rem',
          borderBottom: '1px solid var(--token-border-light, rgba(0, 0, 0, 0.05))',
        }}
      >
        <h3 style={{ fontWeight: 500, color: 'var(--token-text-primary, #0d0d0d)', fontSize: '0.9375rem' }}>
          全局设置
        </h3>
        <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)', marginTop: '0.125rem' }}>
          新建会话时的默认配置
        </p>
      </div>

      {/* Content */}
      <div style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem', flex: 1 }}>
        {/* Default Provider */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            默认提供商
          </label>
          <select
            value={defaultProvider}
            onChange={(e) => {
              setDefaultProvider(e.target.value)
              setDefaultModel('')
            }}
            style={{
              width: '100%',
              padding: '0.625rem 0.875rem',
              border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
              borderRadius: '0.75rem',
              fontSize: '0.875rem',
              color: 'var(--token-text-primary, #0d0d0d)',
              background: 'var(--token-main-surface-primary, #fff)',
              outline: 'none',
              transition: 'border-color 0.15s, box-shadow 0.15s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--token-text-accent, #3a83f7)'
              e.target.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
              e.target.style.boxShadow = 'none'
            }}
          >
            <option value="">无默认值（每次选择）</option>
            {providers.filter(p => p.is_active).map(provider => (
              <option key={provider.id} value={provider.id}>
                {provider.name} ({provider.provider_type})
              </option>
            ))}
          </select>
          {providers.length === 0 && (
            <p style={{ fontSize: '0.75rem', color: '#d97706' }}>尚未配置提供商，请先添加一个提供商。</p>
          )}
        </div>

        {/* Default Model */}
        {defaultProvider && availableModels.length > 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
              默认模型
            </label>
            <select
              value={defaultModel}
              onChange={(e) => setDefaultModel(e.target.value)}
              style={{
                width: '100%',
                padding: '0.625rem 0.875rem',
                border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
                borderRadius: '0.75rem',
                fontSize: '0.875rem',
                color: 'var(--token-text-primary, #0d0d0d)',
                background: 'var(--token-main-surface-primary, #fff)',
                outline: 'none',
                transition: 'border-color 0.15s, box-shadow 0.15s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--token-text-accent, #3a83f7)'
                e.target.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
                e.target.style.boxShadow = 'none'
              }}
            >
              <option value="">使用提供商默认</option>
              {availableModels.map(model => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Temperature */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
              默认温度
            </label>
            <span style={{ fontSize: '0.875rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
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
            style={{
              width: '100%',
              height: '0.375rem',
              background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))',
              borderRadius: '9999px',
              appearance: 'none',
              cursor: 'pointer',
            }}
          />
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.6875rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
            <span>精确 (0)</span>
            <span>创意 (2)</span>
          </div>
        </div>

        {/* Max Tokens */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            默认最大 Token 数
          </label>
          <input
            type="number"
            min="1"
            max="128000"
            value={maxTokens}
            onChange={(e) => setMaxTokens(parseInt(e.target.value) || 2048)}
            style={{
              width: '100%',
              padding: '0.625rem 0.875rem',
              border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
              borderRadius: '0.75rem',
              fontSize: '0.875rem',
              color: 'var(--token-text-primary, #0d0d0d)',
              outline: 'none',
              transition: 'border-color 0.15s, box-shadow 0.15s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--token-text-accent, #3a83f7)'
              e.target.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
              e.target.style.boxShadow = 'none'
            }}
          />
          <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
            模型回复的最大 Token 数量
          </p>
        </div>

        {/* System Prompt */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            默认系统提示词
          </label>
          <textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="你是一个有帮助的助手..."
            rows={4}
            style={{
              width: '100%',
              padding: '0.75rem 0.875rem',
              border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
              borderRadius: '0.75rem',
              fontSize: '0.875rem',
              fontFamily: 'var(--font-mono, ui-monospace, monospace)',
              color: 'var(--token-text-primary, #0d0d0d)',
              resize: 'none',
              outline: 'none',
              transition: 'border-color 0.15s, box-shadow 0.15s',
            }}
            onFocus={(e) => {
              e.target.style.borderColor = 'var(--token-text-accent, #3a83f7)'
              e.target.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
            }}
            onBlur={(e) => {
              e.target.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
              e.target.style.boxShadow = 'none'
            }}
          />
          <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
            此提示词将用于所有新建会话，除非被单独覆盖
          </p>
        </div>

        {/* Database Table Whitelist */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            数据库表白名单
          </label>
          <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
            允许数据库查询工具访问的表（只读）
          </p>

          {/* Add Table Input */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              value={newTable}
              onChange={(e) => setNewTable(e.target.value)}
              onKeyDown={handleTableKeyDown}
              placeholder="table_name"
              style={{
                flex: 1,
                padding: '0.625rem 0.875rem',
                border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
                borderRadius: '0.75rem',
                fontSize: '0.875rem',
                fontFamily: 'var(--font-mono, ui-monospace, monospace)',
                color: 'var(--token-text-primary, #0d0d0d)',
                outline: 'none',
                transition: 'border-color 0.15s, box-shadow 0.15s',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'var(--token-text-accent, #3a83f7)'
                e.target.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
                e.target.style.boxShadow = 'none'
              }}
            />
            <button
              onClick={handleAddTable}
              disabled={!newTable.trim()}
              style={{
                padding: '0.625rem 1rem',
                background: newTable.trim() ? 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))' : 'var(--token-surface-tertiary, rgba(0, 0, 0, 0.02))',
                color: newTable.trim() ? 'var(--token-text-primary, #0d0d0d)' : 'var(--token-text-tertiary, #8f8f8f)',
                borderRadius: '0.75rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                border: 'none',
                cursor: newTable.trim() ? 'pointer' : 'default',
                transition: 'background 0.15s',
              }}
            >
              添加
            </button>
          </div>

          {/* Whitelist Tags */}
          {allowedTables.length > 0 && (
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.5rem' }}>
              {allowedTables.map(table => (
                <span
                  key={table}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.375rem',
                    padding: '0.25rem 0.625rem',
                    background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.04))',
                    color: 'var(--token-text-primary, #0d0d0d)',
                    borderRadius: '0.5rem',
                    fontSize: '0.8125rem',
                    fontFamily: 'var(--font-mono, ui-monospace, monospace)',
                  }}
                >
                  {table}
                  <button
                    onClick={() => handleRemoveTable(table)}
                    style={{
                      color: 'var(--token-text-tertiary, #8f8f8f)',
                      background: 'none',
                      border: 'none',
                      padding: 0,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      transition: 'color 0.15s',
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.color = '#dc2626'}
                    onMouseLeave={(e) => e.currentTarget.style.color = 'var(--token-text-tertiary, #8f8f8f)'}
                  >
                    <svg style={{ width: '0.875rem', height: '0.875rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer - 常驻，只有修改后可点击 */}
      <div
        style={{
          padding: '0.875rem 1.25rem',
          borderTop: '1px solid var(--token-border-light, rgba(0, 0, 0, 0.05))',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '0.5rem',
          background: 'var(--token-surface-secondary, rgba(0, 0, 0, 0.02))',
        }}
      >
        <button
          onClick={handleReset}
          disabled={!hasChanges}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: hasChanges ? 'var(--token-text-secondary, #5d5d5d)' : 'var(--token-text-tertiary, #8f8f8f)',
            background: 'transparent',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: hasChanges ? 'pointer' : 'default',
            transition: 'color 0.15s',
            opacity: hasChanges ? 1 : 0.5,
          }}
          onMouseEnter={(e) => hasChanges && (e.currentTarget.style.color = 'var(--token-text-primary, #0d0d0d)')}
          onMouseLeave={(e) => hasChanges && (e.currentTarget.style.color = 'var(--token-text-secondary, #5d5d5d)')}
        >
          重置
        </button>
        <button
          onClick={handleSave}
          disabled={!hasChanges || isSaving}
          style={{
            padding: '0.5rem 1rem',
            fontSize: '0.875rem',
            fontWeight: 500,
            color: '#fff',
            background: hasChanges && !isSaving ? 'var(--token-text-primary, #0d0d0d)' : 'var(--token-text-tertiary, #8f8f8f)',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: hasChanges && !isSaving ? 'pointer' : 'default',
            transition: 'background 0.15s',
            opacity: hasChanges ? 1 : 0.5,
          }}
        >
          {isSaving ? '保存中...' : '保存更改'}
        </button>
      </div>
    </div>
  )
}
