# LLM Chat Application - Phase 3 & Phase 4 & Phase 8 Tasks

## Status Legend
- [x] Completed
- [ ] Not Started
- [~] In Progress

---

## Phase 8: Agent Frontend Integration

### 10.1 创建工具调用卡片组件（显示工具名、参数、状态）
- [x] Created `frontend/src/components/chat/ToolCallCard.tsx`
- [x] Displays tool icon, name, and status (pending, running, success, error, timeout)
- [x] Shows tool arguments in formatted JSON
- [x] Supports expandable result display

### 10.2 实现工具执行中/成功/失败/超时状态显示
- [x] Status-specific styling:
  - Running: Blue theme with spinning indicator and progress bar
  - Success: Green theme with checkmark icon
  - Error: Red theme with error message display
  - Timeout: Orange theme with timeout message
- [x] Duration display when start/end times available

### 10.3 实现工具结果详情展开/折叠
- [x] Default collapsed, shows result count
- [x] Click to expand/collapse
- [x] JSON result formatting with syntax highlighting
- [x] Special handling for array results (like search results)
- [x] Max height with scrolling for long results

### 10.4 创建会话工具设置组件（工具开关列表）
- [x] Created `frontend/src/components/chat/ToolSettings.tsx`
- [x] Tool list grouped by category
- [x] Toggle switches for each tool
- [x] Select all / Clear all buttons
- [x] Tool count display

### 10.5 实现会话工具配置持久化
- [x] Created `frontend/src/hooks/useToolConfig.ts`
- [x] LocalStorage persistence for tool configuration
- [x] Per-session tool settings support
- [x] Global default tool settings
- [x] Reset functionality

---

## Phase 3: Model Provider Abstraction

### 3.1 Define ModelProvider Protocol/Interface
- [x] Created `backend/app/providers/base.py`
- [x] Defined `ModelProvider` protocol with `chat()`, `chat_stream()`, `list_models()`, `validate_connection()` methods
- [x] Defined supporting types: `ChatMessage`, `ModelInfo`, `ToolCall`, `ToolResult`, `ProviderConfig`, `ChatCompletionResult`
- [x] Defined exception types: `ProviderError`, `ProviderNotFoundError`, `ModelNotFoundError`

### 3.2 Implement LlamaCppProvider (OpenAI Compatible API)
- [x] Created `backend/app/providers/llama_cpp.py`
- [x] Inherits from `BaseOpenAICompatibleProvider`
- [x] Default endpoint: `http://localhost:8080`
- [x] Supports function calling (configurable)
- [x] Model listing with fallback

### 3.3 Implement OpenAIProvider
- [x] Created `backend/app/providers/openai.py`
- [x] Inherits from `BaseOpenAICompatibleProvider`
- [x] Default endpoint: `https://api.openai.com/v1`
- [x] Known model capabilities (GPT-4, GPT-3.5, GPT-4o, o1)
- [x] Tool support detection per model

### 3.4 Implement CustomProvider (Generic OpenAI Compatible)
- [x] Created `backend/app/providers/custom.py`
- [x] Inherits from `BaseOpenAICompatibleProvider`
- [x] Configurable endpoint
- [x] Multiple authentication formats (bearer, api_key, custom header)
- [x] Parameter transformation support
- [x] Model configuration fallback

### 3.5 Implement Provider Factory and Registration Mechanism
- [x] Created `backend/app/providers/factory.py`
- [x] `ProviderFactory` class with register/unregister/create methods
- [x] Global factory singleton
- [x] Convenience functions: `create_provider()`, `register_provider()`

### 3.6 Implement Model List Retrieval API
- [x] Each provider implements `list_models()` returning `List[ModelInfo]`
- [x] OpenAI-compatible providers use `/v1/models` endpoint
- [x] Fallback to configured models when API unavailable

---

## Phase 4: Tool System

### 4.1 Define Tool Protocol/Interface
- [x] Created `backend/app/tools/base.py`
- [x] Defined `Tool` protocol with `name`, `description`, `parameters`, `execute()` methods
- [x] Defined `BaseTool` abstract class with common functionality
- [x] Defined `ToolResult` dataclass
- [x] Defined exception types: `ToolError`, `ToolTimeoutError`, `ToolNotAllowedError`, `ToolExecutionError`
- [x] Defined `ToolRegistry` for tool management

### 4.2 Implement ToolExecutor
- [x] Created `backend/app/tools/executor.py`
- [x] Tool registration with `register()` method
- [x] Whitelist checking with `is_allowed()` method
- [x] Execution dispatch with parameter validation
- [x] Timeout control using `asyncio.wait_for()`
- [x] Per-tool timeout configuration
- [x] `ToolExecutorBuilder` for fluent configuration
- [x] OpenAI format export with `get_openai_tools()`

### 4.3 Implement WebSearchTool (DuckDuckGo Integration)
- [x] Created `backend/app/tools/web_search.py`
- [x] Uses `duckduckgo-search` library
- [x] 30 second default timeout
- [x] Configurable max results (default 5, max 20)
- [x] Region configuration support
- [x] Formatted output for model consumption

### 4.4 Implement DbQueryTool (Read-Only SQL)
- [x] Created `backend/app/tools/db_query.py`
- [x] Read-only SELECT queries only
- [x] Forbidden operations: INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER, CREATE, GRANT, REVOKE, EXEC, CALL
- [x] Table whitelist: [sessions, messages, tool_calls]
- [x] 10 second default timeout
- [x] 100 row default limit (max 1000)
- [x] SQL injection prevention via pattern matching
- [x] Multiple statement prevention

### 4.5 Implement Function Calling Message Format Adaptation
- [x] Created `backend/app/tools/tool_calling.py`
- [x] `format_tool_call_message()` - formats tool call as assistant message
- [x] `format_tool_result_message()` - formats tool result as tool message
- [x] `messages_to_openai_format()` - converts ChatMessage to OpenAI format

### 4.6 Implement Tool Calling Loop
- [x] Created `ToolCallLoop` class
- [x] Loop flow: model -> tool call -> execute -> result -> model
- [x] Max iterations configuration (default 10)
- [x] `run()` method for non-streaming execution
- [x] `run_stream()` method for streaming final response
- [x] `ToolCallLoopResult` with final content and message history
- [x] Convenience functions: `execute_tool_call()`, `build_tool_call_history()`

---

## Phase 5: Backend API

### 5.1 Implement Session Management API (CRUD, with tool configuration)
- [x] Created `backend/app/api/sessions.py`
- [x] `POST /api/sessions` - Create session
- [x] `GET /api/sessions` - List sessions with pagination
- [x] `GET /api/sessions/{id}` - Get single session
- [x] `PUT /api/sessions/{id}` - Update session
- [x] `DELETE /api/sessions/{id}` - Delete session
- [x] Created `backend/app/services/session_service.py`
- [x] Created `backend/app/schemas/api.py` with SessionCreate, SessionUpdate, SessionResponse

### 5.2 Implement Message Management API
- [x] Created `backend/app/api/messages.py`
- [x] `GET /api/sessions/{id}/messages` - Get session messages
- [x] `POST /api/sessions/{id}/messages` - Add message to session
- [x] `DELETE /api/sessions/{id}/messages/{message_id}` - Delete message
- [x] Created `backend/app/services/message_service.py`

### 5.3 Implement Chat API (POST /chat, SSE streaming, Agent events)
- [x] Created `backend/app/api/chat.py`
- [x] `POST /api/chat` - Chat endpoint with SSE streaming
- [x] SSE event types:
  - `content_delta: {"delta": "text"}` - Streaming content
  - `tool_call_start: {"tool_name": "...", "tool_call_id": "..."}` - Tool call start
  - `tool_call_end: {"tool_call_id": "...", "status": "..."}` - Tool call end
  - `done: {}` - Conversation complete
  - `error: {"message": "...", "code": "..."}` - Error handling
- [x] Tool executor integration with web_search and db_query tools
- [x] Provider configuration from session or global config

### 5.4 Implement Provider Configuration API
- [x] Created `backend/app/api/providers.py`
- [x] `GET /api/providers` - List providers
- [x] `POST /api/providers` - Create provider
- [x] `PUT /api/providers/{id}` - Update provider
- [x] `DELETE /api/providers/{id}` - Delete provider
- [x] API key encryption/decryption support
- [x] Created `backend/app/services/provider_service.py`

### 5.5 Implement Global Configuration API
- [x] Created `backend/app/api/config.py`
- [x] `GET /api/config` - Get global configuration
- [x] `PUT /api/config` - Update global configuration
- [x] `POST /api/config/reset` - Reset to defaults
- [x] Default parameters: temperature, max_tokens, system_prompt
- [x] Tool configuration: allowed tables, timeouts, limits

### 5.6 Implement Health Check API
- [x] Updated `backend/app/api/health.py`
- [x] `GET /health` - Basic health check
- [x] `GET /health/db` - Database connectivity check
- [x] `GET /health/ready` - Kubernetes readiness probe
- [x] `GET /health/live` - Kubernetes liveness probe

### 5.7 Configure CORS Middleware
- [x] Updated `backend/app/main.py` with CORS middleware
- [x] Configured allowed origins from settings
- [x] Support for credentials
- [x] Allow all methods and headers
- [x] Expose streaming headers
- [x] Updated `backend/app/core/config.py` with expanded CORS origins

---

## File Structure

```
backend/app/
├── api/
│   ├── __init__.py          # Router exports
│   ├── health.py            # Health check endpoints
│   ├── sessions.py          # Session management API
│   ├── messages.py          # Message management API
│   ├── chat.py              # Chat API with SSE streaming
│   ├── providers.py         # Provider configuration API
│   └── config.py            # Global configuration API
├── core/
│   ├── __init__.py
│   ├── config.py            # Application settings
│   └── database.py          # Database session management
├── models/
│   ├── __init__.py
│   └── models.py            # SQLAlchemy models
├── providers/
│   ├── __init__.py          # Module exports
│   ├── base.py              # ModelProvider protocol and types
│   ├── openai_compatible.py # Base class for OpenAI-compatible providers
│   ├── llama_cpp.py         # LlamaCpp provider
│   ├── openai.py            # OpenAI provider
│   ├── custom.py            # Custom provider
│   └── factory.py           # Provider factory
├── schemas/
│   ├── __init__.py          # Module exports
│   ├── chat.py              # Chat-related Pydantic schemas
│   └── api.py               # API request/response schemas
├── services/
│   ├── __init__.py          # Service exports
│   ├── config_service.py    # Configuration service
│   ├── session_service.py   # Session management service
│   ├── message_service.py   # Message management service
│   └── provider_service.py  # Provider management service
├── tools/
│   ├── __init__.py          # Module exports
│   ├── base.py              # Tool protocol and types
│   ├── executor.py          # ToolExecutor implementation
│   ├── web_search.py        # DuckDuckGo web search tool
│   ├── db_query.py          # Database query tool
│   └── tool_calling.py      # Tool calling loop and message formatting
├── utils/
│   ├── __init__.py
│   └── encryption.py        # API key encryption utilities
└── main.py                  # FastAPI application entry point
```

---

## API Endpoints

```
POST   /api/sessions                    - Create session
GET    /api/sessions                    - List sessions
GET    /api/sessions/{id}               - Get session
PUT    /api/sessions/{id}               - Update session
DELETE /api/sessions/{id}               - Delete session

GET    /api/sessions/{id}/messages      - Get session messages
POST   /api/sessions/{id}/messages      - Add message
DELETE /api/sessions/{id}/messages/{mid} - Delete message

POST   /api/chat                        - Chat (SSE streaming)

GET    /api/providers                   - List providers
POST   /api/providers                   - Create provider
GET    /api/providers/{id}              - Get provider
PUT    /api/providers/{id}              - Update provider
DELETE /api/providers/{id}              - Delete provider

GET    /api/config                      - Get global config
PUT    /api/config                      - Update global config
POST   /api/config/reset                - Reset to defaults

GET    /health                          - Basic health check
GET    /health/db                       - Database health check
GET    /health/ready                    - Readiness probe
GET    /health/live                     - Liveness probe
```

---

## SSE Event Design

```
Event Types:
- content_delta: {"delta": "文本内容"} - 流式输出
- tool_call_start: {"tool_name": "xxx", "tool_call_id": "xxx"} - 工具调用开始
- tool_call_end: {"tool_call_id": "xxx", "status": "success"} - 工具调用结束
- done: {} - 对话完成
- error: {"message": "..."} - 错误发生
```

---

## Design Decisions

### Provider Architecture
- All providers use OpenAI message format for consistency
- `BaseOpenAICompatibleProvider` provides common HTTP client and parsing logic
- Each provider can override specific behaviors (auth headers, parameter transforms)

### Tool System
- Protocol-based design allows easy extension
- Whitelist provides security layer
- Timeout control prevents runaway tool execution
- Tool results include metadata for debugging

### Security Controls
- DbQueryTool: Regex-based forbidden operation detection
- Table whitelist enforced before query execution
- Row limits prevent memory exhaustion
- Multiple statement detection prevents SQL injection
- API keys encrypted before storage using Fernet symmetric encryption

### API Design
- FastAPI dependency injection for services
- Async/await throughout for efficiency
- SSE streaming for real-time chat responses
- Comprehensive error handling with structured error events

---

## Dependencies Required

```txt
# Core
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0

# For WebSearchTool
duckduckgo-search>=4.0.0

# For HTTP requests (providers)
httpx>=0.25.0

# For encryption
cryptography>=41.0.0
```

---

## Next Steps

1. Add authentication middleware
2. Implement rate limiting
3. Add request/response logging
4. Create frontend application
5. Add WebSocket support for bidirectional communication
6. Implement conversation export/import
