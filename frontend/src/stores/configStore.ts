import { create } from 'zustand'
import { Provider, GlobalConfig, CreateProviderData } from '@/types'
import { apiClient } from '@/api/client'

interface ConfigStore {
  providers: Provider[]
  globalConfig: GlobalConfig | null
  isLoading: boolean
  error: string | null

  // Provider actions
  fetchProviders: () => Promise<void>
  createProvider: (data: CreateProviderData) => Promise<Provider>
  updateProvider: (id: string, data: Partial<Provider>) => Promise<Provider>
  deleteProvider: (id: string) => Promise<void>
  testProviderConnection: (id: string) => Promise<{ success: boolean; message: string }>

  // Global config actions
  fetchGlobalConfig: () => Promise<void>
  updateGlobalConfig: (data: Partial<GlobalConfig>) => Promise<void>

  clearError: () => void
}

export const useConfigStore = create<ConfigStore>((set) => ({
  providers: [],
  globalConfig: null,
  isLoading: false,
  error: null,

  fetchProviders: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<{ providers: Provider[]; total: number }>('/providers')
      set({ providers: response.providers, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch providers',
        isLoading: false
      })
    }
  },

  createProvider: async (data: CreateProviderData) => {
    set({ isLoading: true, error: null })
    try {
      const provider = await apiClient.post<Provider>('/providers', data)
      set(state => ({
        providers: [...state.providers, provider],
        isLoading: false
      }))
      return provider
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to create provider',
        isLoading: false
      })
      throw error
    }
  },

  updateProvider: async (id: string, data: Partial<Provider>) => {
    set({ isLoading: true, error: null })
    try {
      const provider = await apiClient.patch<Provider>(`/providers/${id}`, data)
      set(state => ({
        providers: state.providers.map(p => p.id === id ? provider : p),
        isLoading: false
      }))
      return provider
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update provider',
        isLoading: false
      })
      throw error
    }
  },

  deleteProvider: async (id: string) => {
    set({ isLoading: true, error: null })
    try {
      await apiClient.delete(`/providers/${id}`)
      set(state => ({
        providers: state.providers.filter(p => p.id !== id),
        isLoading: false
      }))
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to delete provider',
        isLoading: false
      })
    }
  },

  testProviderConnection: async (id: string) => {
    try {
      const result = await apiClient.post<{ success: boolean; message: string }>(
        `/providers/${id}/test`
      )
      return result
    } catch (error) {
      return {
        success: false,
        message: error instanceof Error ? error.message : 'Connection test failed'
      }
    }
  },

  fetchGlobalConfig: async () => {
    set({ isLoading: true, error: null })
    try {
      const config = await apiClient.get<GlobalConfig>('/config')
      set({ globalConfig: config, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to fetch global config',
        isLoading: false
      })
    }
  },

  updateGlobalConfig: async (data: Partial<GlobalConfig>) => {
    set({ isLoading: true, error: null })
    try {
      const config = await apiClient.patch<GlobalConfig>('/config', data)
      set({ globalConfig: config, isLoading: false })
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to update global config',
        isLoading: false
      })
    }
  },

  clearError: () => {
    set({ error: null })
  }
}))
