// Session types
export interface Session {
  id: string
  title: string
  provider_id: string | null
  model: string | null
  temperature: number | null
  max_tokens: number | null
  system_prompt: string | null
  enabled_tools: string[]
  created_at: string
  updated_at: string
}

export interface CreateSessionData {
  title?: string
  provider_id?: string
  model?: string
  temperature?: number
  max_tokens?: number
  system_prompt?: string
  enabled_tools?: string[]
}

// Message types
// Note: 'tool' role messages are internal and should be filtered out when displaying
export interface Message {
  id: string
  session_id: string
  role: 'user' | 'assistant' | 'system' | 'tool'
  content: string
  tool_calls: ToolCall[]
  created_at: string
}

export interface ToolCall {
  id: string
  message_id: string
  tool_name: string
  arguments: Record<string, unknown>
  status: 'pending' | 'running' | 'success' | 'error' | 'timeout'
  result: string | null
  error: string | null
  started_at: string | null
  completed_at: string | null
}

// Provider types
export interface Provider {
  id: string
  name: string
  provider_type: string
  base_url: string | null
  is_active: boolean
  config: Record<string, unknown>
  created_at: string
}

export interface CreateProviderData {
  name: string
  provider_type: string
  base_url?: string
  api_key?: string
  config?: Record<string, unknown>
}

// Global config types
export interface GlobalConfig {
  default_provider: string | null
  default_model: string | null
  default_temperature: number
  default_max_tokens: number
  default_system_prompt: string
  db_query_allowed_tables: string[]
  web_search_timeout_seconds: number
  web_search_max_results: number
  db_query_timeout_seconds: number
  db_query_max_rows: number
}

// SSE Event types
export interface SSEEvent {
  type: 'content_delta' | 'tool_call_start' | 'tool_call_end' | 'done' | 'error'
  data: unknown
}

export interface ContentDeltaData {
  content: string
}

export interface ToolCallStartData {
  tool_call_id: string
  tool_name: string
  arguments: Record<string, unknown>
}

export interface ToolCallEndData {
  tool_call_id: string
  status: 'success' | 'error' | 'timeout'
  result: string | null
  error: string | null
}

export interface ErrorData {
  message: string
  code?: string
}
