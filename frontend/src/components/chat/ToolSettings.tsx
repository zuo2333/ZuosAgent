import { useState, useEffect } from 'react'

// Tool definition interface
interface ToolDefinition {
  id: string
  name: string
  description: string
  icon: string
  category: 'search' | 'database' | 'utility' | 'external'
  requiresConfig?: boolean
  configSchema?: Record<string, { type: string; label: string; default: unknown }>
}

// Available tools definition
const AVAILABLE_TOOLS: ToolDefinition[] = [
  {
    id: 'web_search',
    name: 'Web Search',
    description: 'Search the web for current information using DuckDuckGo',
    icon: '🔍',
    category: 'search',
  },
  {
    id: 'db_query',
    name: 'Database Query',
    description: 'Query the database with read-only SELECT statements',
    icon: '🗄️',
    category: 'database',
  },
]

// Tool category display names
const CATEGORY_NAMES: Record<string, string> = {
  search: '搜索工具',
  database: '数据库工具',
  utility: '实用工具',
  external: '外部工具',
}

interface ToolSettingsProps {
  enabledTools: string[]
  onToolsChange: (tools: string[]) => void
  disabled?: boolean
}

export function ToolSettings({ enabledTools, onToolsChange, disabled = false }: ToolSettingsProps) {
  const [localEnabled, setLocalEnabled] = useState<string[]>(enabledTools)

  // Sync with parent state
  useEffect(() => {
    setLocalEnabled(enabledTools)
  }, [enabledTools])

  const handleToggle = (toolId: string) => {
    if (disabled) return

    const newEnabled = localEnabled.includes(toolId)
      ? localEnabled.filter((id) => id !== toolId)
      : [...localEnabled, toolId]

    setLocalEnabled(newEnabled)
    onToolsChange(newEnabled)
  }

  const handleSelectAll = () => {
    if (disabled) return
    const allToolIds = AVAILABLE_TOOLS.map((t) => t.id)
    setLocalEnabled(allToolIds)
    onToolsChange(allToolIds)
  }

  const handleClearAll = () => {
    if (disabled) return
    setLocalEnabled([])
    onToolsChange([])
  }

  // Group tools by category
  const toolsByCategory = AVAILABLE_TOOLS.reduce((acc, tool) => {
    if (!acc[tool.category]) {
      acc[tool.category] = []
    }
    acc[tool.category].push(tool)
    return acc
  }, {} as Record<string, ToolDefinition[]>)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h3
            className="text-sm font-medium"
            style={{ color: 'var(--token-text-primary)' }}
          >
            工具设置
          </h3>
          <p
            className="text-xs"
            style={{ color: 'var(--token-text-tertiary)', marginTop: '2px' }}
          >
            启用后，AI 可以使用这些工具来获取信息
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button
            onClick={handleSelectAll}
            disabled={disabled}
            className="text-xs transition-colors"
            style={{
              color: disabled ? 'var(--token-text-tertiary)' : 'var(--color-link)',
            }}
          >
            全选
          </button>
          <span style={{ color: 'var(--token-border-medium)' }}>|</span>
          <button
            onClick={handleClearAll}
            disabled={disabled}
            className="text-xs transition-colors"
            style={{
              color: disabled ? 'var(--token-text-tertiary)' : 'var(--color-link)',
            }}
          >
            清空
          </button>
        </div>
      </div>

      {/* Tool list by category */}
      {Object.entries(toolsByCategory).map(([category, tools]) => (
        <div key={category} style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <h4
            className="text-xs font-medium uppercase tracking-wide"
            style={{ color: 'var(--token-text-tertiary)' }}
          >
            {CATEGORY_NAMES[category] || category}
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {tools.map((tool) => {
              const isEnabled = localEnabled.includes(tool.id)
              return (
                <label
                  key={tool.id}
                  className={`flex items-center gap-3 p-3 rounded-lg border transition-all cursor-pointer ${
                    disabled ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                  style={{
                    borderColor: isEnabled ? 'var(--color-link)' : 'var(--token-border-light)',
                    background: isEnabled ? 'var(--token-surface-tertiary)' : 'transparent',
                  }}
                >
                  <input
                    type="checkbox"
                    checked={isEnabled}
                    onChange={() => handleToggle(tool.id)}
                    disabled={disabled}
                    className="w-4 h-4 rounded focus:ring-2"
                    style={{
                      accentColor: 'var(--color-link)',
                      marginLeft: '8px',
                      marginRight:'-6px',
                    }}
                  />
                  <div className="flex-1 min-w-0">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="text-base" role="img" aria-label={tool.name}>
                        {tool.icon}
                      </span>
                      <span
                        className="text-sm font-medium"
                        style={{ color: 'var(--token-text-primary)' }}
                      >
                        {tool.name}
                      </span>
                    </div>
                    <p
                      className="text-xs"
                      style={{
                        color: 'var(--token-text-tertiary)',
                        marginTop: '0',
                        marginBottom: '2px',
                      }}
                    >
                      {tool.description}
                    </p>
                  </div>
                </label>
              )
            })}
          </div>
        </div>
      ))}

      {/* Enabled count */}
      <div
        className="text-xs"
        style={{
          color: 'var(--token-text-tertiary)',
          paddingTop: '0.5rem',
          borderTop: '1px solid var(--token-border-light)',
        }}
      >
        已启用 {localEnabled.length} / {AVAILABLE_TOOLS.length} 个工具
      </div>
    </div>
  )
}

export default ToolSettings
