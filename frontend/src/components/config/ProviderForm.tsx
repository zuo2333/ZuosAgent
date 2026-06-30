import { useState, useEffect } from 'react'
import { Provider, CreateProviderData } from '@/types'

interface ProviderFormProps {
  provider?: Provider
  onSave: (data: CreateProviderData) => Promise<void>
  onTest?: (id: string) => Promise<{ success: boolean; message: string }>
  onCancel: () => void
  isSaving?: boolean
}

type ProviderType = 'llama_cpp' | 'openai' | 'custom'

interface FormData {
  name: string
  provider_type: ProviderType
  base_url: string
  api_key: string
  default_model: string
}

export function ProviderForm({
  provider,
  onSave,
  onTest,
  onCancel,
  isSaving = false,
}: ProviderFormProps) {
  const [formData, setFormData] = useState<FormData>({
    name: '',
    provider_type: 'llama_cpp',
    base_url: '',
    api_key: '',
    default_model: '',
  })
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [isTesting, setIsTesting] = useState(false)
  const [errors, setErrors] = useState<Partial<Record<keyof FormData, string>>>({})

  // Initialize form with existing provider data
  useEffect(() => {
    if (provider) {
      setFormData({
        name: provider.name,
        provider_type: provider.provider_type as ProviderType,
        base_url: provider.base_url || '',
        api_key: '', // API key is not returned from backend for security
        default_model: (provider.config?.default_model as string) || '',
      })
    }
  }, [provider])

  // Reset test result when form data changes
  useEffect(() => {
    setTestResult(null)
  }, [formData])

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof FormData, string>> = {}

    if (!formData.name.trim()) {
      newErrors.name = '请输入名称'
    }

    if (formData.provider_type === 'llama_cpp' || formData.provider_type === 'custom') {
      if (!formData.base_url.trim()) {
        newErrors.base_url = '此类型提供商需要填写 Base URL'
      } else {
        try {
          new URL(formData.base_url)
        } catch {
          newErrors.base_url = '请输入有效的 URL'
        }
      }
    }

    if (formData.provider_type === 'openai' && !provider) {
      if (!formData.api_key.trim()) {
        newErrors.api_key = 'OpenAI 需要填写 API Key'
      }
    }

    if (!formData.default_model.trim()) {
      newErrors.default_model = '请输入模型名称'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    const data: CreateProviderData = {
      name: formData.name.trim(),
      provider_type: formData.provider_type,
      config: {
        default_model: formData.default_model.trim(),
      },
    }

    if (formData.provider_type !== 'openai' && formData.base_url.trim()) {
      data.base_url = formData.base_url.trim()
    }

    if (formData.api_key.trim()) {
      data.api_key = formData.api_key.trim()
    }

    await onSave(data)
  }

  const handleTest = async () => {
    if (!provider || !onTest) return

    setIsTesting(true)
    setTestResult(null)

    try {
      const result = await onTest(provider.id)
      setTestResult(result)
    } catch {
      setTestResult({ success: false, message: '连接测试失败' })
    } finally {
      setIsTesting(false)
    }
  }

  const providerTypeOptions = [
    {
      value: 'llama_cpp',
      label: 'Llama.cpp（本地）',
      description: '使用 llama.cpp 服务器进行本地推理',
      needsBaseUrl: true,
      needsApiKey: false,
    },
    {
      value: 'openai',
      label: 'OpenAI',
      description: 'OpenAI API（GPT-4、GPT-3.5 等）',
      needsBaseUrl: false,
      needsApiKey: true,
    },
    {
      value: 'custom',
      label: '自定义提供商',
      description: '兼容 OpenAI 的 API（千帆、DeepSeek 等）',
      needsBaseUrl: true,
      needsApiKey: true,
    },
  ]

  const selectedType = providerTypeOptions.find(t => t.value === formData.provider_type)

  const inputStyle = {
    width: '100%',
    padding: '0.625rem 0.875rem',
    border: `1px solid ${errors.name || errors.base_url || errors.api_key || errors.default_model ? 'rgba(220, 38, 38, 0.3)' : 'var(--token-border-default, rgba(0, 0, 0, 0.1))'}`,
    borderRadius: '0.75rem',
    fontSize: '0.875rem',
    color: 'var(--token-text-primary, #0d0d0d)',
    background: 'var(--token-main-surface-primary, #fff)',
    outline: 'none',
    transition: 'border-color 0.15s, box-shadow 0.15s',
  }

  const focusStyle = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.currentTarget.style.borderColor = 'var(--token-text-accent, #3a83f7)'
    e.currentTarget.style.boxShadow = '0 0 0 3px rgba(58, 131, 247, 0.1)'
  }

  const blurStyle = (e: React.FocusEvent<HTMLInputElement | HTMLSelectElement>) => {
    e.currentTarget.style.borderColor = 'var(--token-border-default, rgba(0, 0, 0, 0.1))'
    e.currentTarget.style.boxShadow = 'none'
  }

  return (
    <div
      style={{
        background: 'var(--token-main-surface-primary, #fff)',
        borderRadius: '1rem',
        border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
        overflow: 'hidden',
        maxWidth: '32rem',
        width: '100%',
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
          {provider ? '编辑提供商' : '添加提供商'}
        </h3>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Provider Type */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            类型
          </label>
          <select
            value={formData.provider_type}
            onChange={(e) => setFormData(prev => ({ ...prev, provider_type: e.target.value as ProviderType }))}
            disabled={!!provider}
            style={{
              ...inputStyle,
              cursor: provider ? 'not-allowed' : 'pointer',
              opacity: provider ? 0.6 : 1,
            }}
            onFocus={focusStyle}
            onBlur={blurStyle}
          >
            {providerTypeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          {selectedType && (
            <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
              {selectedType.description}
            </p>
          )}
        </div>

        {/* Name */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            名称
          </label>
          <input
            type="text"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            placeholder="我的提供商"
            style={inputStyle}
            onFocus={focusStyle}
            onBlur={blurStyle}
          />
          {errors.name && (
            <p style={{ fontSize: '0.75rem', color: '#dc2626' }}>{errors.name}</p>
          )}
        </div>

        {/* Default Model */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
            模型名称
          </label>
          <input
            type="text"
            value={formData.default_model}
            onChange={(e) => setFormData(prev => ({ ...prev, default_model: e.target.value }))}
            placeholder="gpt-4o、qwen-plus、llama-3 等"
            style={{ ...inputStyle, fontFamily: 'var(--font-mono, ui-monospace, monospace)' }}
            onFocus={focusStyle}
            onBlur={blurStyle}
          />
          {errors.default_model && (
            <p style={{ fontSize: '0.75rem', color: '#dc2626' }}>{errors.default_model}</p>
          )}
          <p style={{ fontSize: '0.75rem', color: 'var(--token-text-tertiary, #8f8f8f)' }}>
            此提供商使用的模型标识符（如 gpt-4o、qwen-plus）
          </p>
        </div>

        {/* Base URL (for llama_cpp and custom) */}
        {selectedType?.needsBaseUrl && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
              Base URL
            </label>
            <input
              type="text"
              value={formData.base_url}
              onChange={(e) => setFormData(prev => ({ ...prev, base_url: e.target.value }))}
              placeholder="http://localhost:8080/v1"
              style={{ ...inputStyle, fontFamily: 'var(--font-mono, ui-monospace, monospace)' }}
              onFocus={focusStyle}
              onBlur={blurStyle}
            />
            {errors.base_url && (
              <p style={{ fontSize: '0.75rem', color: '#dc2626' }}>{errors.base_url}</p>
            )}
          </div>
        )}

        {/* API Key (for openai and custom) */}
        {selectedType?.needsApiKey && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.8125rem', fontWeight: 500, color: 'var(--token-text-secondary, #5d5d5d)' }}>
              API Key
              {provider && (
                <span style={{ color: 'var(--token-text-tertiary, #8f8f8f)', fontWeight: 400, marginLeft: '0.25rem' }}>
                  （留空保持不变）
                </span>
              )}
            </label>
            <input
              type="password"
              value={formData.api_key}
              onChange={(e) => setFormData(prev => ({ ...prev, api_key: e.target.value }))}
              placeholder="sk-..."
              style={{ ...inputStyle, fontFamily: 'var(--font-mono, ui-monospace, monospace)' }}
              onFocus={focusStyle}
              onBlur={blurStyle}
            />
            {errors.api_key && (
              <p style={{ fontSize: '0.75rem', color: '#dc2626' }}>{errors.api_key}</p>
            )}
          </div>
        )}

        {/* Test Result */}
        {testResult && (
          <div
            style={{
              padding: '0.75rem 1rem',
              borderRadius: '0.75rem',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              background: testResult.success
                ? 'rgba(16, 185, 129, 0.06)'
                : 'rgba(239, 68, 68, 0.06)',
              color: testResult.success ? '#059669' : '#dc2626',
              border: `1px solid ${testResult.success ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)'}`,
            }}
          >
            {testResult.success ? (
              <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : (
              <svg style={{ width: '1.25rem', height: '1.25rem' }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            )}
            <span>{testResult.message}</span>
          </div>
        )}

        {/* Actions */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '1rem',
            marginTop: '0.5rem',
            borderTop: '1px solid var(--token-border-light, rgba(0, 0, 0, 0.05))',
          }}
        >
          <div>
            {provider && onTest && (
              <button
                type="button"
                onClick={handleTest}
                disabled={isTesting}
                style={{
                  padding: '0.5rem 0.75rem',
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  color: isTesting ? 'var(--token-text-tertiary, #8f8f8f)' : 'var(--token-text-secondary, #5d5d5d)',
                  background: 'transparent',
                  border: 'none',
                  borderRadius: '0.5rem',
                  cursor: isTesting ? 'default' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'color 0.15s',
                }}
              >
                {isTesting ? (
                  <>
                    <div
                      style={{
                        width: '1rem',
                        height: '1rem',
                        borderRadius: '50%',
                        border: '2px solid var(--token-text-accent, #3a83f7)',
                        borderTopColor: 'transparent',
                        animation: 'spin 1s linear infinite',
                      }}
                    />
                    测试中...
                  </>
                ) : (
                  '测试连接'
                )}
              </button>
            )}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              type="button"
              onClick={onCancel}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'var(--token-text-secondary, #5d5d5d)',
                background: 'transparent',
                border: '1px solid var(--token-border-default, rgba(0, 0, 0, 0.1))',
                borderRadius: '0.5rem',
                cursor: 'pointer',
                transition: 'background 0.15s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.background = 'var(--token-surface-hover, rgba(0, 0, 0, 0.03))'}
              onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSaving}
              style={{
                padding: '0.5rem 1rem',
                fontSize: '0.875rem',
                fontWeight: 500,
                color: '#fff',
                background: isSaving ? 'var(--token-text-tertiary, #8f8f8f)' : 'var(--token-text-primary, #0d0d0d)',
                border: 'none',
                borderRadius: '0.5rem',
                cursor: isSaving ? 'default' : 'pointer',
                transition: 'background 0.15s',
              }}
            >
              {isSaving ? '保存中...' : (provider ? '保存更改' : '添加提供商')}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
