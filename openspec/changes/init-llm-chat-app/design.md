## 上下文

构建一个本地运行的 LLM 聊天 Web 应用，核心约束：

- **部署环境**：Docker Compose，本地一键启动
- **硬件资源**：V100 GPU 服务器运行 llama.cpp
- **用户场景**：单用户本地使用，无需认证系统
- **模型源**：本地 llama.cpp + OpenAI API + 自定义 API
- **首个集成模型**：Qwen 3.6（原生支持 Function Calling）

## 目标 / 非目标

**目标：**
- 提供流畅的聊天体验，支持流式输出
- 统一抽象多个模型源，用户可自由切换
- 持久化对话历史，支持会话管理
- 简单部署，Docker Compose 一键启动

**非目标：**
- 多用户系统 / 权限管理
- 移动端适配（优先桌面端）
- 模型微调 / 训练功能

## 决策

### 1. 架构模式：三层架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│                   React + TypeScript + Vite                  │
│                      (端口 5173)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/SSE
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        Backend                               │
│                      FastAPI + Python                        │
│                      (端口 8000)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLAlchemy + asyncpg
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                       PostgreSQL                             │
│                      (端口 5432)                             │
└─────────────────────────────────────────────────────────────┘
```

**理由**：清晰的关注点分离，便于独立开发和测试。

### 2. 模型提供者抽象

```python
# 统一接口设计
class ModelProvider(Protocol):
    async def chat(
        messages: list[ChatMessage],
        model: str,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        ...

    async def list_models() -> list[ModelInfo]:
        ...
```

**实现方案**：

| Provider | 协议 | 端点 |
|----------|------|------|
| LlamaCppProvider | OpenAI 兼容 | http://localhost:8080 |
| OpenAIProvider | OpenAI API | https://api.openai.com |
| CustomProvider | OpenAI 兼容 | 用户配置 |

**理由**：llama.cpp server 提供 OpenAI 兼容 API，统一适配成本最低。

### 3. 流式输出：Server-Sent Events

```
Frontend                Backend                 Model Provider
   │                       │                          │
   │──── POST /chat ──────▶│                          │
   │                       │──── stream request ─────▶│
   │◀─── SSE chunk ────────│◀───── token ─────────────│
   │◀─── SSE chunk ────────│◀───── token ─────────────│
   │◀─── SSE done ─────────│◀───── [DONE] ───────────│
   │                       │                          │
```

**理由**：SSE 比 WebSocket 更简单，适合单向数据流，原生支持断线重连。

### 4. 数据模型

```sql
-- 全局配置表
CREATE TABLE global_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB,
    updated_at TIMESTAMP
);

-- 默认配置示例：
-- 'default_provider': 'local-llama'
-- 'default_model': 'qwen3.6:27b'
-- 'default_temperature': 0.7
-- 'default_max_tokens': 4096
-- 'default_system_prompt': 'You are a helpful assistant.'

-- 会话表
CREATE TABLE sessions (
    id UUID PRIMARY KEY,
    title VARCHAR(100),  -- 限制标题长度
    provider_id VARCHAR(100),
    model VARCHAR(100),
    system_prompt TEXT,  -- 会话级系统提示词
    temperature DECIMAL(3,2),  -- 会话级温度参数
    max_tokens INTEGER,  -- 会话级最大生成长度
    enabled_tools JSONB DEFAULT '["web_search", "db_query"]'::jsonb,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- 消息表
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role VARCHAR(20),  -- user, assistant, system, tool
    content TEXT,
    tool_calls JSONB,  -- 工具调用请求（assistant 消息）
    tool_call_id VARCHAR(100),  -- 工具调用 ID（tool 消息）
    created_at TIMESTAMP
);

-- 提供者配置表
CREATE TABLE providers (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255),
    provider_type VARCHAR(50),  -- llama_cpp, openai, custom
    endpoint VARCHAR(500),
    api_key VARCHAR(500),  -- 加密存储
    config JSONB,
    is_active BOOLEAN DEFAULT true
);

-- 工具调用记录表
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id),
    tool_name VARCHAR(100),
    tool_input JSONB,
    tool_output JSONB,
    status VARCHAR(20),  -- success, failed, denied, timeout
    duration_ms INTEGER,  -- 执行耗时
    created_at TIMESTAMP
);

-- 数据库查询表白名单配置（存储在 global_config）
-- 'db_query_allowed_tables': ['sessions', 'messages', 'tool_calls']
```

### 5. 前端技术选型

| 技术 | 选择 | 理由 |
|------|------|------|
| 构建工具 | Vite | 极速 HMR，现代标配 |
| 状态管理 | Zustand | 轻量，无需 Redux 复杂度 |
| 样式 | TailwindCSS | 快速开发，无需写 CSS 文件 |
| Markdown | react-markdown + remark-gfm | GitHub 风格渲染 |
| 代码高亮 | react-syntax-highlighter | 支持多语言主题 |
| HTTP 客户端 | ky / fetch | 轻量，原生支持 SSE |

### 6. Agent 工具执行架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Agent 执行流程                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   用户消息 ──▶ 模型分析 ──▶ 需要调用工具？                  │
│                                  │                          │
│                        ┌─────────┴─────────┐                │
│                        ▼                   ▼                │
│                       是                  否                │
│                        │                   │                │
│                        ▼                   │                │
│                  检查白名单                 │                │
│                        │                   │                │
│                 ┌──────┴──────┐            │                │
│                 ▼             ▼            │                │
│               允许          禁止           │                │
│                 │             │            │                │
│                 ▼             ▼            │                │
│            执行工具       返回错误         │                │
│                 │             │            │                │
│                 ▼             └────────────┤                │
│            工具结果                       │                │
│                 │                         │                │
│                 └─────────────────────────┤                │
│                                           ▼                │
│                                     生成最终回复            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**核心组件**：

```python
# 工具协议定义
class Tool(Protocol):
    name: str
    description: str
    parameters: dict  # JSON Schema

    async def execute(self, **params) -> ToolResult:
        ...

# 工具执行器
class ToolExecutor:
    def __init__(self, whitelist: list[str]):
        self.tools: dict[str, Tool] = {}
        self.whitelist = whitelist

    async def execute(self, tool_name: str, params: dict) -> ToolResult:
        if tool_name not in self.whitelist:
            return ToolResult(error="Tool not allowed")
        return await self.tools[tool_name].execute(**params)
```

**工具实现**：

| 工具 | 实现方式 | 安全限制 |
|------|----------|----------|
| web_search | DuckDuckGo (duckduckgo-search 库) | 无敏感操作 |
| db_query | SQLAlchemy 只读查询 | 仅 SELECT，表白名单，结果行数限制 |

### 8. Agent SSE 事件设计

Agent 模式下，SSE 需要传递多种事件类型：

```
┌─────────────────────────────────────────────────────────────┐
│                    SSE 事件类型                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  事件: content_delta                                        │
│  data: {"delta": "你好"}                                    │
│  → 文本内容增量（流式输出）                                  │
│                                                             │
│  事件: tool_call_start                                      │
│  data: {"tool_name": "web_search", "tool_call_id": "xxx"}  │
│  → 工具调用开始                                             │
│                                                             │
│  事件: tool_call_end                                        │
│  data: {"tool_call_id": "xxx", "status": "success"}        │
│  → 工具调用结束                                             │
│                                                             │
│  事件: done                                                 │
│  data: {}                                                   │
│  → 对话完成                                                 │
│                                                             │
│  事件: error                                                │
│  data: {"message": "..."}                                   │
│  → 错误发生                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**前端处理流程**：
1. 收到 `tool_call_start` → 显示工具调用卡片（加载状态）
2. 收到 `tool_call_end` → 更新卡片状态
3. 收到 `content_delta` → 流式显示文本
4. 收到 `done` → 完成本次对话

### 9. 工具配置与安全限制

```yaml
# 工具配置默认值
tools:
  web_search:
    enabled: true
    timeout_seconds: 30
    max_results: 5
    provider: duckduckgo

  db_query:
    enabled: true
    timeout_seconds: 10
    max_rows: 100
    allowed_tables:
      - sessions
      - messages
      - tool_calls
    readonly: true
```

**安全限制**：
- db_query 禁止执行 INSERT/UPDATE/DELETE/DROP/TRUNCATE
- db_query 禁止访问系统表（pg_*）
- 所有工具执行有超时限制，超时后强制终止

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| llama.cpp server 未启动时前端报错 | 后端健康检查，前端显示友好提示 |
| 大模型响应慢导致连接超时 | 配置合理的 timeout，显示加载动画 |
| API Key 明文存储 | 使用加密存储，或仅存本地不落库 |
| PostgreSQL 数据丢失 | Docker volume 持久化，定期备份 |
| Agent 工具执行异常 | 工具白名单机制，执行超时限制，错误捕获 |
| 数据库查询泄露敏感数据 | 只读限制，表白名单配置，结果行数上限 |

## 部署架构

```yaml
# docker-compose.yml 概念结构
services:
  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

  backend:
    build: ./backend
    ports: ["8001:8001"]
    depends_on: [postgres]
    environment:
      DATABASE_URL: postgresql://...

  postgres:
    image: postgres:15
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: llm_chat
      POSTGRES_USER: ...
      POSTGRES_PASSWORD: ...
```

## 待定事项

- [ ] 是否支持图片输入（多模态）
- [ ] 是否支持对话导出（Markdown/JSON）
- [ ] 是否支持 Prompt 模板管理
