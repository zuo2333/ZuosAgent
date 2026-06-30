export const meta = {
  name: 'init-llm-chat-app',
  description: 'LLM 聊天应用完整实现工作流',
  phases: [
    { title: 'Phase 1: 项目初始化', detail: '创建项目结构和基础配置' },
    { title: 'Phase 2: 后端数据层', detail: '数据库模型和迁移' },
    { title: 'Phase 3: 核心抽象层', detail: '模型提供者和工具执行' },
    { title: 'Phase 4: 后端 API', detail: 'RESTful API 和 SSE' },
    { title: 'Phase 5: 前端基础', detail: '架构和状态管理' },
    { title: 'Phase 6: 聊天界面', detail: 'UI 组件和交互' },
    { title: 'Phase 7: 会话与配置', detail: '管理功能' },
    { title: 'Phase 8: Agent 集成', detail: '工具调用前端' },
    { title: 'Phase 9: 部署与测试', detail: 'Docker 和验证' },
  ],
}

// Phase 1: 项目初始化
phase('Phase 1: 项目初始化')

const phase1Tasks = [
  '1.1 创建项目根目录结构（frontend/、backend/、docker-compose.yml）',
  '1.2 配置 Docker Compose（postgres、backend、frontend 服务）',
  '1.3 初始化前端项目（Vite + React + TypeScript）',
  '1.4 初始化后端项目（FastAPI + Poetry/requirements.txt）',
  '1.5 配置 PostgreSQL 数据库初始化脚本',
  '1.6 配置环境变量管理（.env 文件、配置模板）',
]

const phase1Result = await agent(`实现 LLM 聊天应用的 Phase 1 项目初始化任务。

任务列表：
${phase1Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

技术栈：
- 前端：React + TypeScript + Vite
- 后端：FastAPI + Python
- 数据库：PostgreSQL
- 部署：Docker Compose

要求：
1. 创建完整的项目目录结构
2. 配置 Docker Compose 包含 postgres、backend、frontend 服务
3. 初始化前端 Vite + React + TypeScript 项目
4. 初始化后端 FastAPI 项目结构
5. 创建数据库初始化脚本
6. 配置环境变量管理

请按照任务顺序依次实现，每完成一个任务后更新 openspec/changes/init-llm-chat-app/tasks.md 中对应的复选框。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase1-init',
  phase: 'Phase 1: 项目初始化',
})

log(`Phase 1 完成: ${phase1Result}`)

// Phase 2: 后端数据层
phase('Phase 2: 后端数据层')

const phase2Tasks = [
  '2.1 配置 SQLAlchemy 异步引擎和会话',
  '2.2 创建数据库模型（GlobalConfig、Session、Message、Provider、ToolCall）',
  '2.3 实现 Alembic 数据库迁移',
  '2.4 实现 API Key 加密存储工具',
  '2.5 初始化全局配置默认数据',
]

const phase2Result = await agent(`实现 LLM 聊天应用的 Phase 2 后端数据层任务。

任务列表：
${phase2Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

数据库模型设计（参考 design.md）：

1. global_config 表：
   - key VARCHAR(100) PRIMARY KEY
   - value JSONB
   - updated_at TIMESTAMP

2. sessions 表：
   - id UUID PRIMARY KEY
   - title VARCHAR(100)
   - provider_id VARCHAR(100)
   - model VARCHAR(100)
   - system_prompt TEXT
   - temperature DECIMAL(3,2)
   - max_tokens INTEGER
   - enabled_tools JSONB DEFAULT '["web_search", "db_query"]'
   - created_at TIMESTAMP
   - updated_at TIMESTAMP

3. messages 表：
   - id UUID PRIMARY KEY
   - session_id UUID FK
   - role VARCHAR(20)
   - content TEXT
   - tool_calls JSONB
   - tool_call_id VARCHAR(100)
   - created_at TIMESTAMP

4. providers 表：
   - id VARCHAR(100) PRIMARY KEY
   - name VARCHAR(255)
   - provider_type VARCHAR(50)
   - endpoint VARCHAR(500)
   - api_key VARCHAR(500) -- 加密存储
   - config JSONB
   - is_active BOOLEAN

5. tool_calls 表：
   - id UUID PRIMARY KEY
   - session_id UUID FK
   - message_id UUID FK
   - tool_name VARCHAR(100)
   - tool_input JSONB
   - tool_output JSONB
   - status VARCHAR(20)
   - duration_ms INTEGER
   - created_at TIMESTAMP

要求：
1. 使用 SQLAlchemy 2.0 异步模式
2. 配置 asyncpg 驱动
3. 实现 API Key 加密存储（使用 cryptography 库）
4. 配置 Alembic 迁移

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase2-data',
  phase: 'Phase 2: 后端数据层',
  })

log(`Phase 2 完成: ${phase2Result}`)

// Phase 3: 核心抽象层（模型提供者 + Agent 工具）
phase('Phase 3: 核心抽象层')

const phase3Tasks = [
  '3.1 定义 ModelProvider 协议/接口',
  '3.2 实现 LlamaCppProvider（OpenAI 兼容 API）',
  '3.3 实现 OpenAIProvider',
  '3.4 实现 CustomProvider（通用 OpenAI 兼容）',
  '3.5 实现 Provider 工厂和注册机制',
  '3.6 实现模型列表获取 API',
  '4.1 定义 Tool 协议/接口（name、description、parameters、execute）',
  '4.2 实现 ToolExecutor（工具注册、白名单检查、执行调度、超时控制）',
  '4.3 实现 WebSearchTool（DuckDuckGo 集成，30秒超时）',
  '4.4 实现 DbQueryTool（只读 SQL，表白名单，10秒超时，100行限制）',
  '4.5 实现 Function Calling 消息格式适配（OpenAI 格式）',
  '4.6 实现工具调用循环（模型 → 工具调用 → 执行 → 结果返回 → 模型继续）',
]

const phase3Result = await agent(`实现 LLM 聊天应用的 Phase 3 核心抽象层任务。

任务列表：
${phase3Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## ModelProvider 接口设计：

\`\`\`python
class ModelProvider(Protocol):
    async def chat(
        messages: list[ChatMessage],
        model: str,
        stream: bool = True
    ) -> AsyncIterator[str] | str:
        ...

    async def list_models() -> list[ModelInfo]:
        ...
\`\`\`

Provider 实现：
- LlamaCppProvider: OpenAI 兼容 API，端点 http://localhost:8080
- OpenAIProvider: 标准 OpenAI API
- CustomProvider: 用户自定义 OpenAI 兼容端点

## Tool 接口设计：

\`\`\`python
class Tool(Protocol):
    name: str
    description: str
    parameters: dict  # JSON Schema

    async def execute(self, **params) -> ToolResult:
        ...

class ToolExecutor:
    def __init__(self, whitelist: list[str]):
        self.tools: dict[str, Tool] = {}
        self.whitelist = whitelist

    async def execute(self, tool_name: str, params: dict) -> ToolResult:
        if tool_name not in self.whitelist:
            return ToolResult(error="Tool not allowed")
        return await self.tools[tool_name].execute(**params)
\`\`\`

工具实现：
- WebSearchTool: DuckDuckGo (duckduckgo-search 库)，30秒超时
- DbQueryTool: 只读 SQL，表白名单 [sessions, messages, tool_calls]，10秒超时，100行限制

要求：
1. 所有 Provider 统一使用 OpenAI 消息格式
2. Tool 执行需要超时控制（asyncio.wait_for）
3. DbQueryTool 必须禁止 INSERT/UPDATE/DELETE/DROP/TRUNCATE
4. 实现完整的工具调用循环

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase3-core',
  phase: 'Phase 3: 核心抽象层',
  })

log(`Phase 3 完成: ${phase3Result}`)

// Phase 4: 后端 API
phase('Phase 4: 后端 API')

const phase4Tasks = [
  '5.1 实现会话管理 API（CRUD，含工具配置）',
  '5.2 实现消息管理 API',
  '5.3 实现聊天 API（POST /chat，SSE 流式响应，支持 Agent 事件）',
  '5.4 实现提供者配置 API',
  '5.5 实现全局配置 API（默认参数、系统提示词、表白名单）',
  '5.6 实现健康检查 API',
  '5.7 配置 CORS 中间件',
]

const phase4Result = await agent(`实现 LLM 聊天应用的 Phase 4 后端 API 任务。

任务列表：
${phase4Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## SSE 事件设计：

\`\`\`
事件类型：
- content_delta: {"delta": "文本内容"} - 流式输出
- tool_call_start: {"tool_name": "xxx", "tool_call_id": "xxx"} - 工具调用开始
- tool_call_end: {"tool_call_id": "xxx", "status": "success"} - 工具调用结束
- done: {} - 对话完成
- error: {"message": "..."} - 错误发生
\`\`\`

## API 端点设计：

\`\`\`
POST /api/sessions - 创建会话
GET /api/sessions - 获取会话列表
GET /api/sessions/{id} - 获取单个会话
PUT /api/sessions/{id} - 更新会话
DELETE /api/sessions/{id} - 删除会话

GET /api/sessions/{id}/messages - 获取会话消息
POST /api/sessions/{id}/messages - 添加消息

POST /api/chat - 聊天（SSE 流式响应）

GET /api/providers - 获取提供者列表
POST /api/providers - 创建提供者
PUT /api/providers/{id} - 更新提供者
DELETE /api/providers/{id} - 删除提供者

GET /api/config - 获取全局配置
PUT /api/config - 更新全局配置

GET /api/health - 健康检查
\`\`\`

要求：
1. 使用 FastAPI 依赖注入
2. SSE 使用 StreamingResponse
3. 配置 CORS 允许前端域名
4. 所有 API 使用异步处理

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase4-api',
  phase: 'Phase 4: 后端 API',
  })

log(`Phase 4 完成: ${phase4Result}`)

// Phase 5: 前端基础架构
phase('Phase 5: 前端基础架构')

const phase5Tasks = [
  '6.1 配置 TailwindCSS',
  '6.2 创建基础布局组件（侧边栏、主内容区）',
  '6.3 配置 Zustand 状态管理（会话 store、配置 store）',
  '6.4 实现 API 客户端（ky/fetch 封装）',
  '6.5 实现 SSE 客户端工具（支持多事件类型）',
]

const phase5Result = await agent(`实现 LLM 聊天应用的 Phase 5 前端基础架构任务。

任务列表：
${phase5Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

技术栈：
- 构建工具：Vite
- 框架：React + TypeScript
- 样式：TailwindCSS
- 状态管理：Zustand
- HTTP 客户端：原生 fetch

## 布局设计：

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                        应用布局                              │
├────────────────┬────────────────────────────────────────────┤
│                │                                            │
│    侧边栏      │              主内容区                       │
│    (w-64)      │                                            │
│                │   ┌────────────────────────────────────┐   │
│  - 会话列表    │   │        聊天消息区                   │   │
│  - 新建会话    │   │                                     │   │
│  - 设置入口    │   ├────────────────────────────────────┤   │
│                │   │        输入区                       │   │
│                │   └────────────────────────────────────┘   │
│                │                                            │
└────────────────┴────────────────────────────────────────────┘
\`\`\`

## Zustand Store 设计：

\`\`\`typescript
// sessionStore
interface SessionStore {
  sessions: Session[]
  currentSession: Session | null
  fetchSessions: () => Promise<void>
  createSession: (data: CreateSessionData) => Promise<Session>
  deleteSession: (id: string) => Promise<void>
  setCurrentSession: (session: Session | null) => void
}

// configStore
interface ConfigStore {
  providers: Provider[]
  globalConfig: GlobalConfig
  fetchProviders: () => Promise<void>
  fetchGlobalConfig: () => Promise<void>
}
\`\`\`

## SSE 客户端：

\`\`\`typescript
interface SSEEvent {
  type: 'content_delta' | 'tool_call_start' | 'tool_call_end' | 'done' | 'error'
  data: any
}

async function* streamChat(message: string, sessionId: string): AsyncGenerator<SSEEvent>
\`\`\`

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase5-frontend-base',
  phase: 'Phase 5: 前端基础架构',
  })

log(`Phase 5 完成: ${phase5Result}`)

// Phase 6: 聊天界面
phase('Phase 6: 聊天界面')

const phase6Tasks = [
  '7.1 创建消息气泡组件（用户/助手区分）',
  '7.2 实现聊天输入框组件（多行支持、快捷键）',
  '7.3 实现 Markdown 渲染（react-markdown + remark-gfm）',
  '7.4 实现代码高亮（react-syntax-highlighter）',
  '7.5 实现消息复制功能',
  '7.6 实现流式输出显示',
  '7.7 实现停止生成按钮',
]

const phase6Result = await agent(`实现 LLM 聊天应用的 Phase 6 聊天界面任务。

任务列表：
${phase6Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## 组件设计：

### MessageBubble 组件：
- 用户消息：右对齐，蓝色背景
- 助手消息：左对齐，灰色背景
- 支持 Markdown 渲染
- 支持代码块高亮
- 复制按钮

### ChatInput 组件：
- 多行文本输入（textarea）
- Enter 发送，Shift+Enter 换行
- 发送按钮
- 停止生成按钮（生成中显示）

### MarkdownRenderer 组件：
- 使用 react-markdown + remark-gfm
- 代码块使用 react-syntax-highlighter
- 支持复制代码

### StreamingMessage 组件：
- 显示流式输出的内容
- 打字机效果
- 光标闪烁动画

依赖安装：
\`\`\`bash
npm install react-markdown remark-gfm react-syntax-highlighter
npm install @types/react-syntax-highlighter -D
\`\`\`

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase6-chat-ui',
  phase: 'Phase 6: 聊天界面',
  })

log(`Phase 6 完成: ${phase6Result}`)

// Phase 7: 会话与配置管理
phase('Phase 7: 会话与配置管理')

const phase7Tasks = [
  '8.1 创建会话列表组件',
  '8.2 实现新建会话功能',
  '8.3 实现会话切换功能',
  '8.4 实现会话删除功能（含确认对话框）',
  '8.5 实现会话重命名功能（100字符限制）',
  '8.6 实现会话标题自动生成',
  '8.7 实现会话级参数配置（temperature、max_tokens、system_prompt）',
  '9.1 创建提供者配置表单组件',
  '9.2 实现添加/编辑/删除提供者功能',
  '9.3 实现模型选择器组件',
  '9.4 实现全局参数配置（默认 temperature、max_tokens）',
  '9.5 实现默认系统提示词配置',
  '9.6 实现配置验证（API 连接测试）',
]

const phase7Result = await agent(`实现 LLM 聊天应用的 Phase 7 会话与配置管理任务。

任务列表：
${phase7Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## 会话列表组件：

\`\`\`
┌────────────────────┐
│  + 新建会话        │
├────────────────────┤
│ 📝 会话标题 1      │
│    昨天           │
├────────────────────┤
│ 📝 会话标题 2      │
│    今天           │
└────────────────────┘
\`\`\`

功能：
- 按更新时间倒序显示
- 点击切换会话
- 右键菜单：重命名、删除
- 删除需确认对话框

## 会话设置面板：

\`\`\`
┌────────────────────────────────────────┐
│ 会话设置                               │
├────────────────────────────────────────┤
│ 模型：[下拉选择]                       │
│ Temperature: [滑块 0-2]                │
│ Max Tokens: [数字输入]                 │
│ 系统提示词：                           │
│ ┌────────────────────────────────┐     │
│ │ You are a helpful assistant... │     │
│ └────────────────────────────────┘     │
│                                        │
│ 工具设置：                             │
│ ☑️ 网页搜索 (web_search)              │
│ ☑️ 数据库查询 (db_query)              │
└────────────────────────────────────────┘
\`\`\`

## 提供者配置表单：

\`\`\`
┌────────────────────────────────────────┐
│ 添加提供者                             │
├────────────────────────────────────────┤
│ 类型：[llama_cpp / openai / custom]   │
│ 名称：[输入框]                         │
│ 端点：[输入框] (llama_cpp/custom)      │
│ API Key：[密码输入框] (openai/custom)  │
│                                        │
│ [测试连接]  [保存]  [取消]             │
└────────────────────────────────────────┘
\`\`\`

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase7-session-config',
  phase: 'Phase 7: 会话与配置管理',
  })

log(`Phase 7 完成: ${phase7Result}`)

// Phase 8: Agent 前端集成
phase('Phase 8: Agent 前端集成')

const phase8Tasks = [
  '10.1 创建工具调用卡片组件（显示工具名、参数、状态）',
  '10.2 实现工具执行中/成功/失败/超时状态显示',
  '10.3 实现工具结果详情展开/折叠',
  '10.4 创建会话工具设置组件（工具开关列表）',
  '10.5 实现会话工具配置持久化',
]

const phase8Result = await agent(`实现 LLM 聊天应用的 Phase 8 Agent 前端集成任务。

任务列表：
${phase8Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## 工具调用卡片设计：

\`\`\`
┌────────────────────────────────────────┐
│ 🔍 web_search                    ✓ 成功 │
├────────────────────────────────────────┤
│ 参数：{"query": "天气", "num_results": 5} │
├────────────────────────────────────────┤
│ ▼ 结果 (点击展开)                      │
│   - 结果 1: 标题...                    │
│   - 结果 2: 标题...                    │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ 🗄️ db_query                   ⏳ 执行中 │
├────────────────────────────────────────┤
│ 参数：{"sql": "SELECT * FROM sessions"} │
│                                        │
│ ████████████░░░░░░░░░░░ 执行中...      │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ 🗄️ db_query                    ✗ 失败  │
├────────────────────────────────────────┤
│ 参数：{"sql": "DROP TABLE users"}      │
├────────────────────────────────────────┤
│ 错误：只允许 SELECT 查询               │
└────────────────────────────────────────┘
\`\`\`

## 状态显示：

- 执行中：旋转图标 + 灰色背景
- 成功：绿色图标 + 绿色边框
- 失败：红色图标 + 红色边框
- 超时：橙色图标 + 橙色边框

## 结果展示：

- 默认折叠，显示结果数量
- 点击展开显示完整结果
- JSON 结果格式化显示
- 长结果支持滚动

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase8-agent-ui',
  phase: 'Phase 8: Agent 前端集成',
  })

log(`Phase 8 完成: ${phase8Result}`)

// Phase 9: 部署与测试
phase('Phase 9: 部署与测试')

const phase9Tasks = [
  '11.1 配置前端 Dockerfile（多阶段构建）',
  '11.2 配置后端 Dockerfile',
  '11.3 完善 docker-compose.yml 环境变量配置',
  '11.4 编写 README 部署文档',
  '11.5 端到端功能验证',
  '12.1 后端单元测试（ModelProvider、ToolExecutor）',
  '12.2 后端 API 集成测试',
  '12.3 前端组件测试（关键组件）',
  '12.4 Agent 工具测试（WebSearchTool、DbQueryTool 安全限制验证）',
]

const phase9Result = await agent(`实现 LLM 聊天应用的 Phase 9 部署与测试任务。

任务列表：
${phase9Tasks.map((t, i) => `${i + 1}. ${t}`).join('\n')}

## Dockerfile 设计：

### 前端 Dockerfile（多阶段构建）：
\`\`\`dockerfile
# 构建阶段
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 生产阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
\`\`\`

### 后端 Dockerfile：
\`\`\`dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
\`\`\`

## docker-compose.yml 完善：

\`\`\`yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "8001:8001"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/llm_chat
      - ENCRYPTION_KEY=...
    depends_on:
      - postgres

  postgres:
    image: postgres:15
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=llm_chat
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

volumes:
  pgdata:
\`\`\`

## 测试要求：

### 后端单元测试：
- ModelProvider 接口测试
- ToolExecutor 白名单测试
- 加密/解密测试

### 后端集成测试：
- 会话 API 测试
- 聊天 API 测试
- SSE 流式测试

### Agent 工具测试：
- WebSearchTool 功能测试
- DbQueryTool 安全测试（禁止写入、表白名单）

请按照任务顺序依次实现，每完成一个任务后更新 tasks.md。

工作目录：D:\\IdeaProjects\\MyAgent`, {
  label: 'phase9-deploy-test',
  phase: 'Phase 9: 部署与测试',
  })

log(`Phase 9 完成: ${phase9Result}`)

// 完成
log('所有 Phase 完成！项目实现完毕。')

return {
  success: true,
  message: 'LLM 聊天应用已完整实现',
  phases: 9,
  totalTasks: 69,
}
