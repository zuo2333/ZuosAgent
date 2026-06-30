import { useState, useEffect, useRef } from 'react'
import { Provider } from '@/types'

interface ModelSelectorProps {
  providers: Provider[]
  selectedProviderId: string | null
  selectedModel: string | null
  onSelectProvider: (providerId: string | null) => void
  onSelectModel: (model: string | null) => void
  disabled?: boolean
}

export function ModelSelector({
  providers,
  selectedProviderId,
  selectedModel,
  onSelectProvider,
  onSelectModel,
  disabled = false,
}: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const dropdownRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Filter active providers
  const activeProviders = providers.filter(p => p.is_active)

  // Get selected provider data
  const selectedProvider = activeProviders.find(p => p.id === selectedProviderId)

  // Get available models for selected provider
  const availableModels = (selectedProvider?.config?.models as string[]) || []

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  // Filter models based on search query
  const filteredModels = availableModels.filter(model =>
    model.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Get display text
  const getDisplayText = () => {
    if (!selectedProvider) return 'Select a model...'
    if (!selectedModel) return `${selectedProvider.name} - Select model`
    return `${selectedProvider.name} / ${selectedModel}`
  }

  const handleProviderSelect = (providerId: string) => {
    if (providerId === selectedProviderId) return
    onSelectProvider(providerId)
    onSelectModel(null) // Reset model when provider changes
    setSearchQuery('')
    inputRef.current?.focus()
  }

  const handleModelSelect = (model: string) => {
    onSelectModel(model)
    setIsOpen(false)
    setSearchQuery('')
  }

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation()
    onSelectProvider(null)
    onSelectModel(null)
  }

  if (activeProviders.length === 0) {
    return (
      <div
        className="px-3 py-2 rounded-lg text-sm"
        style={{
          border: '1px solid var(--token-border-light)',
          background: 'var(--token-surface-secondary)',
          color: 'var(--token-text-tertiary)',
        }}
      >
        No providers configured
      </div>
    )
  }

  return (
    <div ref={dropdownRef} className="relative">
      {/* Trigger Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className="w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm text-left transition-colors"
        style={{
          border: isOpen ? '1px solid var(--token-border-heavy)' : '1px solid var(--token-border-medium)',
          background: disabled ? 'var(--token-surface-tertiary)' : 'var(--token-surface-primary)',
          color: disabled ? 'var(--token-text-tertiary)' : 'var(--token-text-primary)',
          cursor: disabled ? 'not-allowed' : 'pointer',
        }}
      >
        <span style={{ color: (selectedProvider && selectedModel) ? 'var(--token-text-primary)' : 'var(--token-text-tertiary)' }}>
          {getDisplayText()}
        </span>
        <div className="flex items-center gap-1">
          {selectedProvider && (
            <button
              onClick={handleClear}
              className="p-0.5 rounded"
              style={{ color: 'var(--token-text-tertiary)' }}
              title="Clear selection"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          <svg
            className={`w-5 h-5 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            style={{ color: 'var(--token-text-tertiary)' }}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className="absolute z-50 mt-1 w-full rounded-lg shadow-lg overflow-hidden"
          style={{
            background: 'var(--token-surface-primary)',
            border: '1px solid var(--token-border-light)',
          }}
        >
          {/* Provider Tabs */}
          <div
            className="flex overflow-x-auto"
            style={{ borderBottom: '1px solid var(--token-border-extra-light)' }}
          >
            {activeProviders.map(provider => (
              <button
                key={provider.id}
                onClick={() => handleProviderSelect(provider.id)}
                className="px-3 py-2 text-xs font-medium whitespace-nowrap transition-colors"
                style={{
                  color: selectedProviderId === provider.id ? 'var(--token-text-primary)' : 'var(--token-text-secondary)',
                  borderBottom: selectedProviderId === provider.id ? '2px solid var(--token-text-primary)' : 'none',
                  background: selectedProviderId === provider.id ? 'var(--token-surface-secondary)' : 'transparent',
                }}
              >
                {provider.name}
              </button>
            ))}
          </div>

          {/* Model Search (if provider selected) */}
          {selectedProvider && (
            <div
              className="p-2"
              style={{ borderBottom: '1px solid var(--token-border-extra-light)' }}
            >
              <div className="relative">
                <svg
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-4 h-4"
                  style={{ color: 'var(--token-text-tertiary)' }}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  ref={inputRef}
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search models..."
                  className="w-full pl-8 pr-3 py-1.5 rounded text-sm focus:outline-none"
                  style={{
                    border: '1px solid var(--token-border-light)',
                    background: 'var(--token-surface-primary)',
                    color: 'var(--token-text-primary)',
                  }}
                />
              </div>
            </div>
          )}

          {/* Model List */}
          <div className="max-h-60 overflow-y-auto">
            {!selectedProvider ? (
              <div
                className="p-4 text-center text-sm"
                style={{ color: 'var(--token-text-tertiary)' }}
              >
                Select a provider tab to see available models
              </div>
            ) : filteredModels.length === 0 ? (
              <div
                className="p-4 text-center text-sm"
                style={{ color: 'var(--token-text-tertiary)' }}
              >
                {searchQuery ? 'No models match your search' : 'No models available for this provider'}
              </div>
            ) : (
              <div className="py-1">
                {filteredModels.map(model => (
                  <button
                    key={model}
                    onClick={() => handleModelSelect(model)}
                    className="w-full px-3 py-2 text-left text-sm flex items-center justify-between transition-colors"
                    style={{
                      color: selectedModel === model ? 'var(--token-text-primary)' : 'var(--token-text-secondary)',
                      background: selectedModel === model ? 'var(--token-surface-secondary)' : 'transparent',
                    }}
                  >
                    <span className="font-mono">{model}</span>
                    {selectedModel === model && (
                      <svg
                        className="w-4 h-4"
                        style={{ color: 'var(--color-success)' }}
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
