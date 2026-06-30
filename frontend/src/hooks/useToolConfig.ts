import { useState, useCallback, useEffect } from 'react'

const STORAGE_KEY = 'llm-chat-tool-config'

// Tool configuration interface
export interface ToolConfig {
  enabledTools: string[]
  perSessionSettings: Record<string, string[]>
}

// Default tool configuration
const DEFAULT_CONFIG: ToolConfig = {
  enabledTools: ['web_search'],
  perSessionSettings: {},
}

/**
 * Custom hook for managing tool configuration with persistence
 */
export function useToolConfig(sessionId?: string) {
  const [config, setConfig] = useState<ToolConfig>(() => {
    // Load from localStorage on initialization
    if (typeof window === 'undefined') {
      return DEFAULT_CONFIG
    }

    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        return {
          ...DEFAULT_CONFIG,
          ...parsed,
        }
      }
    } catch (error) {
      console.error('Failed to load tool config from storage:', error)
    }

    return DEFAULT_CONFIG
  })

  // Persist config to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(config))
    } catch (error) {
      console.error('Failed to save tool config to storage:', error)
    }
  }, [config])

  // Get enabled tools for current session (or global default)
  const getEnabledTools = useCallback(
    (sid?: string): string[] => {
      if (sid && config.perSessionSettings[sid]) {
        return config.perSessionSettings[sid]
      }
      return config.enabledTools
    },
    [config]
  )

  // Update global enabled tools
  const setEnabledTools = useCallback((tools: string[]) => {
    setConfig((prev) => ({
      ...prev,
      enabledTools: tools,
    }))
  }, [])

  // Update per-session tool settings
  const setSessionTools = useCallback((sid: string, tools: string[]) => {
    setConfig((prev) => ({
      ...prev,
      perSessionSettings: {
        ...prev.perSessionSettings,
        [sid]: tools,
      },
    }))
  }, [])

  // Clear per-session settings for a specific session
  const clearSessionTools = useCallback((sid: string) => {
    setConfig((prev) => {
      const { [sid]: _, ...rest } = prev.perSessionSettings
      return {
        ...prev,
        perSessionSettings: rest,
      }
    })
  }, [])

  // Reset to default configuration
  const resetConfig = useCallback(() => {
    setConfig(DEFAULT_CONFIG)
  }, [])

  // Get current session's enabled tools
  const currentEnabledTools = sessionId
    ? getEnabledTools(sessionId)
    : config.enabledTools

  return {
    // State
    enabledTools: currentEnabledTools,
    globalEnabledTools: config.enabledTools,
    allConfig: config,

    // Actions
    setEnabledTools,
    setSessionTools,
    clearSessionTools,
    resetConfig,
    getEnabledTools,
  }
}

export default useToolConfig
