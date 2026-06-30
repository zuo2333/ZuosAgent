## 为什么

需要一个完全本地运行的大模型对话网页应用，支持多种模型源（本地 llama.cpp + 云端 API），解决以下问题：

1. 现有聊天工具多为云端服务，数据隐私和成本不可控
2. 本地 LLM 方案（如 llama.cpp）缺乏友好的 Web UI
3. 需要统一接口管理多个模型源，避免在多个工具间切换

## 变更内容

构建一个完整的 LLM 聊天 Web 应用：

- **前端**：React + TypeScript + Vite，提供现代化聊天界面
- **后端**：FastAPI (Python)，提供 API 网关和业务逻辑
- **数据库**：PostgreSQL，持久化对话历史和配置
- **部署**：Docker Compose，一键启动完整服务栈
- **模型源**：支持 llama.cpp（本地 V100）、OpenAI API、自定义 API 端点
- **Agent 能力**：支持工具调用（网页搜索、数据库查询），会话级白名单控制，首个集成模型使用 Qwen 3.6

## 功能 (Capabilities)

### 新增功能

- `chat-interface`: 聊天界面 — 流式输出、Markdown 渲染、代码高亮
- `model-provider`: 模型提供者 — 统一抽象层，支持本地和云端模型
- `session-management`: 会话管理 — 多会话切换、历史保存、会话删除
- `configuration`: 配置管理 — API 密钥管理、模型参数配置
- `agent-tools`: Agent 工具 — 网页搜索、数据库查询，会话级白名单控制

### 修改功能

无（全新项目）

## 影响

- 新建项目，无现有代码影响
- 依赖 Docker 环境运行 PostgreSQL
- 需要本地运行 llama.cpp server（V100 服务器）或配置外部 API
- Agent 网页搜索使用 DuckDuckGo（免费开源，无需 API Key）
- Agent 数据库查询限制为只读，仅允许查询应用自身数据
