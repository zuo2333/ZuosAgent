# LLM Chat - 技术架构深度解析

> 本文档从面试官视角全面剖析项目的技术选型、架构设计、核心实现与创新点。
> 适合用于技术分享、面试准备、新人入职引导。

---

## 目录

1. [项目概述](#一项目概述)
2. [技术栈详解](#二技术栈详解)
3. [架构设计](#三架构设计)
4. [核心设计模式](#四核心设计模式)
5. [记忆系统](#五记忆系统)
6. [创新点与技术亮点](#六创新点与技术亮点)
7. [技术选型对比](#七技术选型对比)
8. [前端架构亮点](#八前端架构亮点)
9. [测试策略](#九测试策略)
10. [部署架构](#十部署架构)
11. [总结](#十一总结)

---

## 一、项目概述

### 1.1 项目定位

这是一个**大模型对话服务平台**，提供类似 ChatGPT 的对话体验。项目的核心价值在于：

- **多模型接入**：支持 OpenAI、LlamaCpp、自定义端点等多种 LLM 提供者
- **工具调用能力**：AI 可以调用网络搜索、数据库查询等工具获取实时信息
- **流式响应**：实时推送 AI 回复，提升用户体验
- **会话管理**：支持多会话、配置持久化、历史记录

### 1.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面 (Frontend)                        │
│    React 18 + TypeScript + Tailwind CSS v4 + Zustand           │
└────────────────────────────┬────────────────────────────────────┘
                             │ SSE (Server-Sent Events)
                             │ 实时双向通信，流式响应
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     后端服务 (Backend)                           │
│    FastAPI + SQLAlchemy 2.0 + PostgreSQL + Alembic              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Services   │  │   Providers  │  │    Tools     │          │
│  │  业务逻辑层   │  │  模型抽象层   │  │  工具调用层   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ OpenAI   │      │ LlamaCpp │      │ Custom   │
    │ Provider │      │ Provider │      │ Provider │
    │ (GPT-4)  │      │ (本地模型) │      │ (自定义)  │
    └──────────┘      └──────────┘      └──────────┘
```

### 1.3 核心功能模块

| 模块 | 功能描述 | 技术要点 |
|------|----------|----------|
| **会话管理** | 创建、删除、切换对话会话 | RESTful API + PostgreSQL 持久化 |
| **消息流** | 用户发送消息，AI 流式回复 | SSE (Server-Sent Events) |
| **模型切换** | 动态选择不同的 LLM 提供者 | Factory 模式 + Protocol 抽象 |
| **工具调用** | AI 自主决定是否调用工具 | Agent Loop + OpenAI Function Calling |
| **Markdown 渲染** | 富文本展示 AI 回复 | react-markdown + 代码高亮 |

---

## 二、技术栈详解

### 2.1 前端技术栈

```
frontend/
├── package.json          # 依赖管理
├── vite.config.ts        # Vite 构建配置
├── tailwind.config.js    # Tailwind CSS 配置
├── tsconfig.json         # TypeScript 配置
└── src/
    ├── main.tsx          # 应用入口
    ├── App.tsx           # 根组件
    ├── components/       # UI 组件
    ├── stores/           # Zustand 状态管理
    ├── api/              # API 客户端
    ├── utils/            # 工具函数
    └── types/            # TypeScript 类型定义
```

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| **React** | 18.3 | 生态成熟，组件化开发，Concurrent Mode 支持更好的用户体验。选择 React 而非 Vue 是因为团队更熟悉，且 AI 相关的开源项目多为 React 技术栈。 |
| **TypeScript** | 5.6 | 类型安全，IDE 智能提示，大型项目必备。可以在编译时发现大量潜在 bug。 |
| **Vite** | 5.4 | 极速开发体验，ESM 原生支持。相比 Webpack，冷启动快 10-20 倍，热更新几乎是即时的。 |
| **Tailwind CSS** | 4.3 | 原子化 CSS，开发效率高。v4 采用 CSS-first 配置，无需 JS 配置文件，更简洁。 |
| **Zustand** | 5.0 | 轻量级状态管理（~1KB）。相比 Redux 无 boilerplate，相比 MobX 更简单，学习曲线低。 |
| **React Markdown** | 10.1 | Markdown 渲染，支持 GFM（表格、删除线、任务列表等）。配合 react-syntax-highlighter 实现代码高亮。 |
| **Vitest** | 2.1 | Vite 原生测试框架，比 Jest 更快，配置更简单。 |

### 2.2 后端技术栈

```
backend/
├── requirements.txt      # Python 依赖
├── alembic/              # 数据库迁移
│   └── versions/
│       └── 001_initial_schema.py
├── app/
│   ├── main.py           # FastAPI 入口
│   ├── core/             # 核心配置
│   ├── models/           # ORM 模型
│   ├── schemas/          # Pydantic 模型
│   ├── services/         # 业务逻辑
│   ├── api/              # API 路由
│   ├── providers/        # 模型提供者
│   ├── tools/            # 工具调用
│   └── utils/            # 工具函数
└── tests/                # 测试用例
```

| 技术 | 版本 | 选型理由 |
|------|------|----------|
| **FastAPI** | 0.115 | 现代 Python Web 框架，异步原生，自动生成 OpenAPI 文档。相比 Django 更轻量，相比 Flask 性能更高且类型安全。 |
| **SQLAlchemy** | 2.0 | Python ORM 标准，2.0 版本全面支持 async/await。相比 Django ORM 更灵活，相比 raw SQL 更安全。 |
| **AsyncPG** | 0.30 | PostgreSQL 异步驱动，性能优异。相比 psycopg2 快 3-5 倍，且支持连接池。 |
| **Alembic** | 1.14 | 数据库迁移工具，SQLAlchemy 官方推荐。支持版本管理和自动生成迁移脚本。 |
| **Pydantic** | 2.10 | 数据验证和序列化，FastAPI 核心依赖。v2 版本使用 Rust 重写核心，性能提升 5-50 倍。 |
| **httpx** | 0.28 | 现代异步 HTTP 客户端，支持 HTTP/2。相比 requests 支持异步，相比 aiohttp API 更友好。 |
| **cryptography** | 44.0 | API Key 加密存储。使用 Fernet 对称加密，密钥通过 PBKDF2 派生，安全性高。 |

---

## 三、架构设计

### 3.1 后端分层架构

后端采用**分层架构**设计，职责清晰，易于测试和维护：

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (路由层)                        │
│   处理 HTTP 请求，参数验证，响应格式化                             │
│   文件: api/chat.py, api/sessions.py, api/providers.py          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Service Layer (服务层)                       │
│   业务逻辑处理，事务管理，跨模块协调                                │
│   文件: services/session_service.py, services/message_service.py │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Model Layer (数据层)                         │
│   数据库模型定义，ORM 映射                                        │
│   文件: models/models.py (Session, Message, Provider, ToolCall)  │
└─────────────────────────────────────────────────────────────────┘
```

**为什么采用分层架构？**

1. **职责分离**：每层只关注自己的职责，修改一层不影响其他层
2. **易于测试**：可以独立测试每一层，Service 层可以 mock 数据库
3. **代码复用**：Service 层可以被多个 API 调用，避免重复代码
4. **团队协作**：不同团队成员可以并行开发不同层

### 3.2 数据模型设计

```
┌────────────────┐       ┌────────────────┐
│   sessions     │       │    messages    │
├────────────────┤       ├────────────────┤
│ id (UUID)      │◄──────│ session_id (FK)│  一个会话有多条消息
│ title          │  1:N  │ id (UUID)      │
│ provider_id    │       │ role           │  role: user/assistant/system/tool
│ model          │       │ content        │
│ temperature    │       │ tool_calls     │  JSONB: 存储工具调用信息
│ max_tokens     │       │ tool_call_id   │  关联到具体的工具调用
│ system_prompt  │       └────────────────┘
│ enabled_tools  │
└────────────────┘       ┌────────────────┐
                         │  tool_calls    │
┌────────────────┐       ├────────────────┤
│   providers    │       │ session_id (FK)│  工具调用记录
├────────────────┤       │ message_id (FK)│
│ id (PK)        │       │ tool_name      │  工具名称
│ name           │       │ tool_input     │  输入参数 (JSONB)
│ provider_type  │       │ tool_output    │  输出结果 (JSONB)
│ endpoint       │       │ status         │  success/failed/timeout
│ api_key (加密) │       │ duration_ms    │  执行耗时
│ config (JSONB) │       └────────────────┘
└────────────────┘

┌────────────────┐
│ global_config  │  全局配置键值对
├────────────────┤
│ key (PK)       │  如: default_provider, default_model
│ value (JSONB)  │  灵活存储各种配置
└────────────────┘
```

**设计要点**：

1. **UUID 主键**：分布式友好，不易被枚举
2. **JSONB 字段**：灵活存储半结构化数据（tool_calls, config），PostgreSQL JSONB 支持索引和高效查询
3. **外键级联删除**：删除 session 时自动删除关联的 messages 和 tool_calls
4. **加密字段**：api_key 使用 Fernet 对称加密存储，即使数据库泄露也无法直接获取密钥

### 3.3 前端组件架构

```
src/components/
├── layout/                    # 布局组件
│   ├── AppLayout.tsx         # 整体布局：侧边栏 + 主内容区
│   ├── Sidebar.tsx           # 左侧导航栏
│   ├── Header.tsx            # 顶部标题栏
│   └── MainContent.tsx       # 主内容容器
│
├── chat/                      # 聊天相关组件
│   ├── ChatPanel.tsx         # 聊天面板（组合各子组件）
│   ├── MessageList.tsx       # 消息列表（自动滚动）
│   ├── MessageBubble.tsx     # 单条消息气泡
│   ├── StreamingMessage.tsx  # 流式输出中的消息
│   ├── StreamingToolCalls.tsx # 工具调用过程展示
│   ├── MarkdownRenderer.tsx  # Markdown 渲染 + 代码高亮
│   └── ChatInput.tsx         # 输入框 + 发送按钮
│
├── session/                   # 会话管理组件
│   ├── SessionList.tsx       # 会话列表（支持重命名、删除）
│   └── SessionSettings.tsx   # 会话设置面板（模型、温度等）
│
├── config/                    # 配置相关组件
│   ├── ProviderForm.tsx      # 提供者配置表单
│   ├── ProviderList.tsx      # 提供者列表
│   └── GlobalConfigPanel.tsx # 全局配置面板
│
├── settings/                  # 设置页面
│   └── SettingsPage.tsx      # 设置弹窗（整合 Provider 管理）
│
└── ui/                        # 通用 UI 组件
    └── ConfirmDialog.tsx     # 确认对话框
```

---

## 四、核心设计模式

### 4.1 Provider Protocol + Factory Pattern

**问题**：如何支持多种 LLM 提供者（OpenAI、LlamaCpp、自定义），并易于扩展新提供者？

**解决方案**：使用 Protocol 定义接口契约，Factory 负责创建具体实例。

```python
# providers/base.py - 定义接口契约
@runtime_checkable
class ModelProvider(Protocol):
    """所有模型提供者必须实现这个 Protocol"""

    @property
    def provider_id(self) -> str: ...

    @property
    def provider_type(self) -> str: ...

    async def chat(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
    ) -> ChatCompletionResult: ...

    async def chat_stream(
        self, messages, model, ...
    ) -> AsyncIterator[str]: ...

    async def list_models(self) -> List[ModelInfo]: ...

    async def validate_connection(self) -> bool: ...
```

```python
# providers/factory.py - 工厂模式创建实例
class ProviderFactory:
    # 注册表：提供者类型 -> 实现类
    _registry: Dict[str, Type[ModelProvider]] = {
        "llama_cpp": LlamaCppProvider,
        "openai": OpenAIProvider,
        "custom": CustomProvider,
    }

    @classmethod
    def register(cls, provider_type: str, provider_class: Type[ModelProvider]):
        """注册新的提供者类型"""
        cls._registry[provider_type] = provider_class

    def create(self, config: ProviderConfig) -> ModelProvider:
        """根据配置创建提供者实例"""
        provider_class = self._registry[config.provider_type]
        return provider_class(config)
```

**优势**：

1. **开闭原则**：新增提供者只需实现 Protocol 并注册，无需修改现有代码
2. **类型安全**：Python 类型检查器可以验证实现是否完整
3. **配置驱动**：从数据库读取配置，动态创建实例
4. **易于测试**：可以轻松 mock 一个提供者进行测试

**使用示例**：

```python
# 从数据库读取配置
provider_model = await provider_service.get(provider_id)
provider_config = ProviderConfig.from_db_model(provider_model, decrypted_api_key)

# 工厂创建实例
provider = create_provider(provider_config)

# 调用统一接口
result = await provider.chat(messages, model="gpt-4")
```

### 4.2 Tool Protocol + Builder Pattern

**问题**：工具需要注册、白名单控制、超时管理，如何优雅地组合这些功能？

**解决方案**：Protocol 定义接口，Builder 提供流式配置 API。

```python
# tools/base.py - 工具接口
class Tool(Protocol):
    @property
    def name(self) -> str: ...          # 工具名称

    @property
    def description(self) -> str: ...   # 工具描述（给 AI 看）

    @property
    def parameters(self) -> Dict: ...   # 参数 JSON Schema

    async def execute(self, **params) -> ToolResult: ...  # 执行方法
```

```python
# tools/executor.py - Builder 模式
class ToolExecutorBuilder:
    """流式构建工具执行器"""

    def with_whitelist(self, tools: List[str]) -> Self:
        """设置白名单"""
        self._whitelist = tools
        return self

    def with_tool(self, tool: Tool, timeout: float = None) -> Self:
        """注册工具"""
        self._tools.append((tool, timeout))
        return self

    def build(self) -> ToolExecutor:
        """构建执行器"""
        executor = ToolExecutor(whitelist=self._whitelist)
        for tool, timeout in self._tools:
            executor.register(tool, timeout)
        return executor
```

**使用示例**：

```python
# 构建工具执行器
executor = (ToolExecutorBuilder()
    .with_whitelist(["web_search", "db_query"])  # 只允许这两个工具
    .with_tool(WebSearchTool(), timeout=30.0)    # 网络搜索，30秒超时
    .with_tool(DbQueryTool(db_session), timeout=10.0)  # 数据库查询，10秒超时
    .build())

# 执行工具
result = await executor.execute("web_search", {"query": "Python async"})

# 获取 OpenAI 格式的工具定义（传给 LLM）
tools = executor.get_openai_tools()
```

**安全控制**：

```python
# tools/executor.py
async def execute(self, tool_name: str, params: Dict) -> ToolResult:
    # 1. 白名单检查
    if not self.is_allowed(tool_name):
        return ToolResult(error=f"Tool '{tool_name}' is not allowed")

    # 2. 参数校验
    validation_error = tool.validate_parameters(params)
    if validation_error:
        return ToolResult(error=validation_error)

    # 3. 超时执行
    try:
        result = await asyncio.wait_for(
            tool.execute(**params),
            timeout=self.get_timeout(tool_name)
        )
        return result
    except asyncio.TimeoutError:
        return ToolResult(error="Tool execution timed out")
```

### 4.3 OpenAI-Compatible Base Class

**问题**：OpenAI、LlamaCpp、自定义提供者都使用类似的 OpenAI API 格式，如何复用代码？

**解决方案**：抽象基类 + 模板方法模式。

```python
# providers/openai_compatible.py
class BaseOpenAICompatibleProvider(ABC):
    """所有 OpenAI 兼容提供者的基类"""

    async def chat(self, messages, model, ...) -> ChatCompletionResult:
        """模板方法：统一的调用流程"""
        client = self._get_client()

        # 1. 构建请求体（子类可覆盖）
        request_body = {
            "model": model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            **kwargs
        }

        # 2. 发送请求
        response = await client.post(self.chat_path, json=request_body)
        response.raise_for_status()

        # 3. 解析响应（子类可覆盖）
        return self._parse_completion_response(response.json())

    @property
    @abstractmethod
    def base_url(self) -> str:
        """子类必须实现：返回 API 基础地址"""
        ...

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """子类必须实现：返回提供者类型标识"""
        ...
```

```python
# providers/openai.py
class OpenAIProvider(BaseOpenAICompatibleProvider):
    """OpenAI 官方 API 提供者"""

    @property
    def base_url(self) -> str:
        # 支持自定义端点（如 Azure OpenAI）
        return self.config.endpoint or "https://api.openai.com/v1"

    @property
    def provider_type(self) -> str:
        return "openai"

    # 额外的 OpenAI 特定逻辑...
```

**优势**：

1. **代码复用**：HTTP 请求、错误处理、响应解析等通用逻辑在基类实现
2. **易于扩展**：新增提供者只需实现少量差异化代码
3. **统一接口**：所有提供者对外暴露相同的调用方式

### 4.4 依赖注入（Dependency Injection）

**问题**：Service 层需要数据库会话，如何管理其生命周期？

**解决方案**：使用 FastAPI 的 Depends 注入机制。

```python
# core/database.py
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # 成功时提交
        except Exception:
            await session.rollback()  # 失败时回滚
            raise
        finally:
            await session.close()
```

```python
# api/chat.py
def get_session_service(db: AsyncSession = Depends(get_db)) -> SessionService:
    """Service 依赖工厂"""
    return SessionService(db)

@router.post("/chat")
async def chat(
    request: ChatRequest,
    session_service: SessionService = Depends(get_session_service),
    message_service: MessageService = Depends(get_message_service),
    provider_service: ProviderService = Depends(get_provider_service),
):
    # 框架自动注入依赖
    session = await session_service.get(request.session_id)
    ...
```

**优势**：

1. **自动事务管理**：请求成功自动提交，异常自动回滚
2. **易于测试**：测试时可以注入 mock 对象
3. **生命周期管理**：框架负责创建和销毁资源

---

## 五、记忆系统

### 5.1 系统概述

记忆系统为 LLM 提供跨会话的上下文记忆能力，实现个性化对话体验。采用三层架构设计：

```
┌─────────────────────────────────────────────────────────────────┐
│                      MemoryContextService                        │
│                   (整合三层记忆，组装上下文)                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ShortTermMemory  │ │LongTermMemory   │ │UserProfile      │
│Service          │ │Service          │ │Service          │
├─────────────────┤ ├─────────────────┤ ├─────────────────┤
│ - 会话摘要      │ │ - 向量检索      │ │ - 用户偏好      │
│ - 实体提取      │ │ - 重要性评分    │ │ - 行为分析      │
│ - 任务跟踪      │ │ - 遗忘曲线      │ │ - 知识图谱      │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

### 5.2 三层记忆架构

| 层级 | 存储内容 | 检索方式 | 生命周期 |
|------|----------|----------|----------|
| **短期记忆** | 当前会话摘要、实体、待办任务 | 直接查询 | 会话结束 |
| **长期记忆** | 事实、偏好、事件 | 向量语义检索 | 持久化 |
| **用户画像** | 个人偏好、技术水平、知识图谱 | 直接查询 | 持久化 |

### 5.3 核心技术实现

#### 向量检索（pgvector）

```python
# 使用 PostgreSQL pgvector 扩展进行向量存储和检索
CREATE EXTENSION vector;
CREATE INDEX ix_embedding ON long_term_memories
USING hnsw (embedding vector_cosine_ops);
```

**优势**：
- 无需额外部署向量数据库
- 与现有 PostgreSQL 基础设施集成
- HNSW 索引支持高效近似检索

#### 按需记忆注入

记忆注入基于意图分类，避免每轮对话都检索记忆：

```python
class MemoryIntentClassifier:
    # 规则匹配，无 LLM 调用
    NO_MEMORY_PATTERNS = [
        r'^(你好|hi|hello)',      # 问候语无需记忆
        r'^(什么是|解释一下)',     # 知识问答无需记忆
    ]

    LONG_TERM_PATTERNS = [
        r'(上次|以前|曾经)',       # 引用历史
        r'(我喜欢|我的偏好)',      # 偏好相关
    ]
```

#### 遗忘曲线衰减

实现 Ebbinghaus 遗忘曲线，自动降低旧记忆的重要性：

```python
# 衰减公式：decay = e^(-days / half_life)
DECAY_HALF_LIFE_DAYS = 100
decay_factor = math.exp(-days_old * math.log(2) / 100)
```

### 5.4 记忆提取时机

| 触发条件 | 说明 |
|----------|------|
| 会话结束 | 用户关闭/切换会话时触发完整提取 |
| 检查点 | 每 20 条消息触发增量提取 |
| 手动触发 | 用户调用 API 显式提取 |

### 5.5 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| 向量数据库 | pgvector | 无需额外运维，与 PostgreSQL 集成 |
| Embedding | bge-large-zh-v1.5 | 中文效果好，本地部署无 API 成本 |
| 备选 Embedding | text-embedding-3-small | OpenAI 云端方案，配置切换 |

---

## 六、创新点与技术亮点

### 5.1 Agent 循环 + 工具调用流程

这是项目的核心功能之一：AI 可以自主决定调用工具，并根据工具返回结果继续生成回答。

```
┌─────────────────────────────────────────────────────────────────┐
│                        Agent Loop                               │
│                                                                 │
│  用户: "帮我搜索一下 Python 异步编程的最佳实践"                    │
│                                                                 │
│  ┌─────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  User   │───▶│    LLM      │───▶│ Tool Calls? │             │
│  │ Message │    │ Completion  │    │   (判断)     │             │
│  └─────────┘    └─────────────┘    └──────┬──────┘             │
│                                           │                     │
│                      ┌────────────────────┴────────────┐        │
│                      │ Yes                        No  │        │
│                      ▼                                 ▼        │
│               ┌─────────────┐                   ┌──────────┐    │
│               │   Execute   │                   │  Return  │    │
│               │ web_search  │                   │  Content │    │
│               └──────┬──────┘                   └──────────┘    │
│                      │                                          │
│                      ▼                                          │
│               ┌─────────────┐                                   │
│               │ Tool Result │                                   │
│               │  → Message  │                                   │
│               └──────┬──────┘                                   │
│                      │                                          │
│                      ▼                                          │
│               ┌─────────────┐                                   │
│               │ Next Iter.  │◀──────────────────────────────────┘
│               │  (继续调用   │   LLM 看到工具结果后继续生成
│               │   LLM)      │
│               └─────────────┘
│                                                                 │
│  最大迭代次数: 10（防止无限循环）                                  │
└─────────────────────────────────────────────────────────────────┘
```

**后端实现**：

```python
# api/chat.py
async def stream_chat_response(messages, model, ..., tool_executor, provider):
    max_iterations = 10

    for iteration in range(max_iterations):
        # 1. 调用 LLM
        completion = await provider.chat(
            messages=messages,
            model=model,
            tools=tool_executor.get_openai_tools(),  # 传入可用工具
            tool_choice="auto",
        )

        # 2. 判断是否有工具调用
        if completion.tool_calls:
            # 3. 执行所有工具调用
            for tool_call in completion.tool_calls:
                # 发送 SSE 事件：工具开始
                yield format_sse_event("tool_call_start", {
                    "tool_name": tool_call.name,
                    "tool_call_id": tool_call.id,
                })

                # 执行工具
                result = await tool_executor.execute(
                    tool_call.name,
                    tool_call.arguments
                )

                # 发送 SSE 事件：工具结束
                yield format_sse_event("tool_call_end", {
                    "tool_call_id": tool_call.id,
                    "status": "success" if result.is_success else "error",
                    "result": result.to_content(),
                })

                # 将工具结果加入消息历史
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result.to_content(),
                })

            # 继续下一轮迭代，让 LLM 处理工具结果
            continue

        else:
            # 4. 没有工具调用，返回最终答案
            yield format_sse_event("content_delta", {
                "content": completion.content
            })
            yield format_sse_event("done", {})
            return
```

**SSE 事件流示例**：

```
event: tool_call_start
data: {"tool_name": "web_search", "tool_call_id": "call_abc123", "arguments": {"query": "Python async"}}

event: tool_call_end
data: {"tool_call_id": "call_abc123", "status": "success", "result": "[1] Python Async IO Guide..."}

event: content_delta
data: {"content": "根据搜索结果，Python 异步编程的最佳实践包括..."}

event: done
data: {}
```

### 5.2 前端流式响应处理

前端实现了自定义的 SSE 客户端，支持多种事件类型：

```typescript
// utils/sse.ts
export class SSEClient {
  async *streamChat(request: ChatRequest, options?: SSEOptions): AsyncGenerator<SSEEvent> {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',  // 告诉服务器返回 SSE 流
      },
      body: JSON.stringify(request),
    })

    const reader = response.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 解析 SSE 格式: "event: xxx\ndata: xxx\n\n"
      const events = this.parseEvents(buffer)
      buffer = events.remainingBuffer

      for (const event of events.parsed) {
        // 调用对应的回调函数
        this.callHandler(event, options)
        yield event
      }
    }
  }

  private parseEvents(buffer: string): { parsed: SSEEvent[], remainingBuffer: string } {
    const events: SSEEvent[] = []
    const pattern = /event:\s*(\w+)\ndata:\s*(.+?)\n\n/gs

    let match
    while ((match = pattern.exec(buffer)) !== null) {
      events.push({
        type: match[1] as SSEEventType,
        data: JSON.parse(match[2]),
      })
    }

    // 保留未完成的数据
    return { parsed: events, remainingBuffer: buffer.slice(match?.index ?? 0) }
  }
}
```

**使用示例**：

```typescript
// components/chat/ChatPanel.tsx
const handleSend = async (content: string) => {
  const generator = sseClient.streamChat(
    { message: content, session_id: sessionId },
    {
      onContentDelta: (data) => {
        // 追加到当前显示内容
        setCurrentContent(prev => prev + data.content)
      },
      onToolCallStart: (data) => {
        // 显示工具调用开始
        addToolCall({ id: data.tool_call_id, name: data.tool_name, status: 'running' })
      },
      onToolCallEnd: (data) => {
        // 更新工具调用状态
        updateToolCall(data.tool_call_id, { status: data.status, result: data.result })
      },
      onDone: () => {
        // 保存最终消息
        saveMessage(currentContent)
      },
    }
  )

  for await (const event of generator) {
    // 事件已在回调中处理
  }
}
```

### 5.3 API Key 安全存储

API Key 使用 **Fernet 对称加密** 存储，即使数据库泄露也无法直接获取明文：

```python
# utils/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def _get_fernet_key() -> bytes:
    """
    从配置的 ENCRYPTION_KEY 派生 Fernet 密钥

    为什么需要派生？
    - Fernet 要求 32 字节的 URL-safe base64 编码密钥
    - PBKDF2 可以从任意长度的密码派生出安全的密钥
    - 100000 次迭代增加暴力破解难度
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'llm-chat-encryption-salt-v1',  # 固定盐值（生产环境应随机生成并存储）
        iterations=100000,
    )
    return base64.urlsafe_b64encode(
        kdf.derive(settings.ENCRYPTION_KEY.encode())
    )

def encrypt_api_key(api_key: str) -> str:
    """加密 API Key"""
    fernet = Fernet(_get_fernet_key())
    return fernet.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API Key"""
    fernet = Fernet(_get_fernet_key())
    return fernet.decrypt(encrypted_key.encode()).decode()
```

### 5.4 数据库查询工具的安全控制

`db_query` 工具允许 AI 执行 SQL 查询，但做了严格的安全限制：

```python
# tools/db_query.py
class DbQueryTool(BaseTool):
    # 禁止的操作（正则匹配）
    FORBIDDEN_PATTERNS = [
        r'\bINSERT\b',    # 禁止插入
        r'\bUPDATE\b',    # 禁止更新
        r'\bDELETE\b',    # 禁止删除
        r'\bDROP\b',      # 禁止删除表
        r'\bTRUNCATE\b',  # 禁止清空表
        r'\bALTER\b',     # 禁止修改结构
        r'\bCREATE\b',    # 禁止创建
        r';.*\b',         # 禁止多语句（防止注入）
    ]

    # 允许查询的表（白名单）
    _allowed_tables = ["sessions", "messages", "tool_calls"]

    async def execute(self, query: str, **params) -> ToolResult:
        # 1. 验证查询类型
        if not query.strip().upper().startswith("SELECT"):
            return ToolResult(error="Only SELECT queries are allowed")

        # 2. 检查禁止的操作
        for pattern in self._forbidden_regex:
            if pattern.search(query):
                return ToolResult(error="Forbidden operation detected")

        # 3. 提取并验证表名
        tables = self._extract_tables(query)
        for table in tables:
            if table.lower() not in [t.lower() for t in self._allowed_tables]:
                return ToolResult(error=f"Table '{table}' is not allowed")

        # 4. 添加行数限制
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT 100"

        # 5. 执行查询
        results = await self._execute_query(query)
        return ToolResult(output=self._format_results(results))
```

---

## 七、技术选型对比

### 6.1 为什么选择 FastAPI 而非 Django/Flask？

| 维度 | FastAPI | Django | Flask |
|------|---------|--------|-------|
| **异步支持** | 原生 async/await，完美支持 SSE | 需要使用 async 视图，支持不完善 | 需要扩展（如 Quart） |
| **类型系统** | Pydantic 自动验证，IDE 友好 | 需要手动验证或使用 DRF | 需要手动验证 |
| **API 文档** | 自动生成 OpenAPI/Swagger | 需要 DRF + drf-yasg | 需要 Flasgger |
| **性能** | 高（基于 Starlette + Uvicorn） | 中 | 中 |
| **学习曲线** | 中等 | 较高（需要学习 ORM、模板等） | 低 |
| **适用场景** | API 服务、微服务 | 全栈应用、Admin 后台 | 小型应用 |

**结论**：本项目是纯 API 服务，需要高性能异步处理 SSE 流式响应，FastAPI 是最佳选择。

### 6.2 为什么选择 Zustand 而非 Redux/MobX？

| 维度 | Zustand | Redux | MobX |
|------|---------|-------|------|
| **包大小** | ~1KB | ~7KB（+ React-Redux） | ~16KB |
| **Boilerplate** | 极少 | 多（actions, reducers, saga/thunk） | 中等 |
| **学习曲线** | 低 | 高 | 中等 |
| **TypeScript** | 原生支持，无需额外配置 | 需要配置，类型推导复杂 | 需要配置 |
| **异步处理** | 原生 async/await | 需要 thunk 或 saga | 原生支持 |
| **调试工具** | 简单 | Redux DevTools（强大） | MobX DevTools |

**结论**：项目状态相对简单（会话列表、当前会话、消息列表），不需要 Redux 的复杂状态管理。Zustand 足够且更轻量。

### 6.3 为什么选择 PostgreSQL 而非 MongoDB？

| 维度 | PostgreSQL | MongoDB |
|------|------------|---------|
| **数据一致性** | ACID 事务，强一致性 | 最终一致（可配置事务） |
| **复杂查询** | SQL 强大，支持 JOIN、子查询 | 聚合管道复杂，学习曲线高 |
| **JSON 支持** | JSONB（二进制 JSON），支持索引 | 原生支持，性能优秀 |
| **关系数据** | 外键、JOIN，天然适合 | 需要嵌入或引用，查询复杂 |
| **成熟度** | 35+ 年，生态成熟 | 15+ 年 |
| **使用场景** | 关系型数据、复杂查询 | 文档型数据、灵活 Schema |

**结论**：会话-消息是典型的关系数据（一对多），需要外键约束保证数据完整性。PostgreSQL 的 JSONB 用于存储 `tool_calls` 等半结构化数据，两全其美。

### 6.4 为什么选择 SSE 而非 WebSocket？

| 维度 | SSE (Server-Sent Events) | WebSocket |
|------|--------------------------|-----------|
| **通信方向** | 单向（服务器→客户端） | 双向 |
| **协议** | HTTP | WS/WSS（需要握手） |
| **重连机制** | 浏览器自动重连 | 需要手动实现 |
| **代理兼容** | 完全兼容 HTTP 代理 | 可能被阻断 |
| **实现复杂度** | 低（标准 HTTP） | 中（需要维护连接状态） |
| **适用场景** | 服务器推送（新闻、聊天） | 实时双向通信（游戏、协作） |

**结论**：LLM 对话是典型的「用户发送请求→服务器流式响应」模式，不需要双向通信。SSE 更简单，且浏览器自动处理重连。

---

## 八、前端架构亮点

### 7.1 状态管理设计

使用 Zustand 的 `create` 模式，简洁且类型安全：

```typescript
// stores/sessionStore.ts
interface SessionStore {
  // 状态
  sessions: Session[]
  currentSession: Session | null
  messages: Message[]
  isLoading: boolean
  error: string | null

  // Actions
  fetchSessions: () => Promise<void>
  createSession: (data?: CreateSessionData) => Promise<Session>
  deleteSession: (id: string) => Promise<void>
  setCurrentSession: (session: Session | null) => void
  fetchMessages: (sessionId: string) => Promise<void>
  setMessages: (messages: Message[]) => void
  addMessage: (message: Message) => void
}

export const useSessionStore = create<SessionStore>((set, get) => ({
  // 初始状态
  sessions: [],
  currentSession: null,
  messages: [],
  isLoading: false,
  error: null,

  // Actions 实现
  fetchSessions: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await apiClient.get<{ sessions: Session[] }>('/sessions')
      set({ sessions: response.sessions, isLoading: false })
    } catch (error) {
      set({ error: error.message, isLoading: false })
    }
  },

  setCurrentSession: (session) => {
    set({ currentSession: session })
    if (session) {
      // 切换会话时自动加载消息
      get().fetchMessages(session.id)
    }
  },

  // ... 其他 actions
}))
```

**在组件中使用**：

```tsx
function SessionList() {
  // 选择需要的状态和 actions
  const { sessions, currentSession, setCurrentSession, isLoading } = useSessionStore()

  // 也可以细粒度选择，避免不必要的重渲染
  const sessions = useSessionStore(state => state.sessions)
  const setCurrentSession = useSessionStore(state => state.setCurrentSession)

  if (isLoading) return <Spinner />

  return (
    <ul>
      {sessions.map(session => (
        <li
          key={session.id}
          onClick={() => setCurrentSession(session)}
          className={currentSession?.id === session.id ? 'active' : ''}
        >
          {session.title}
        </li>
      ))}
    </ul>
  )
}
```

### 7.2 Markdown 渲染优化

使用 `react-markdown` + `react-syntax-highlighter` 实现富文本渲染：

```tsx
// components/chat/MarkdownRenderer.tsx
export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-sm max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}  // 支持 GitHub 风格 Markdown
        components={{
          // 自定义代码块渲染
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '')
            const isInline = !match && !String(children).includes('\n')

            if (isInline) {
              return <code className="bg-gray-100 px-1 rounded" {...props}>{children}</code>
            }

            // 使用 SyntaxHighlighter 实现代码高亮
            return (
              <CodeBlock language={match?.[1] || 'text'}>
                {String(children).replace(/\n$/, '')}
              </CodeBlock>
            )
          },
          // 自定义表格渲染
          table({ children }) {
            return (
              <div className="overflow-x-auto">
                <table className="min-w-full border">{children}</table>
              </div>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
```

### 7.3 Tailwind CSS v4 配置

Tailwind v4 采用 CSS-first 配置，无需 `tailwind.config.js`：

```css
/* index.css */
@import "tailwindcss";

/* 主题配置 */
@theme {
  --color-primary-500: #0ea5e9;
  --color-primary-600: #0284c7;
  --font-weight-heading: 600;
}

/* 自定义 prose 样式（v4 暂不支持 @tailwindcss/typography 插件） */
.prose {
  color: var(--token-text-primary);
  line-height: 1.5;
  font-size: 1rem;
}

.prose h2 {
  font-size: 1.25em;
  margin-top: 1em;
  margin-bottom: 0.375em;
  font-weight: 600;
}

.prose code {
  background-color: var(--token-surface-tertiary);
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-size: 0.9em;
}
```

---

## 九、测试策略

### 8.1 后端测试

使用 `pytest` + `pytest-asyncio` 进行异步测试：

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient

class TestSessionsAPI:
    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient):
        """测试创建会话"""
        response = await client.post("/api/sessions", json={
            "title": "Test Session",
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session"

    @pytest.mark.asyncio
    async def test_delete_session(self, client: AsyncClient):
        """测试删除会话"""
        # 创建
        create_response = await client.post("/api/sessions", json={"title": "To Delete"})
        session_id = create_response.json()["id"]

        # 删除
        delete_response = await client.delete(f"/api/sessions/{session_id}")
        assert delete_response.status_code == 204

        # 验证已删除
        get_response = await client.get(f"/api/sessions/{session_id}")
        assert get_response.status_code == 404
```

### 8.2 前端测试

使用 `Vitest` + `@testing-library/react`：

```typescript
// components/chat/ChatInput.test.tsx
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ChatInput } from './ChatInput'

describe('ChatInput', () => {
  it('should call onSend when pressing Enter', async () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isStreaming={false} />)

    const input = screen.getByPlaceholderText(/有问题/)
    fireEvent.change(input, { target: { value: 'Hello' } })
    fireEvent.keyDown(input, { key: 'Enter', code: 'Enter' })

    expect(onSend).toHaveBeenCalledWith('Hello')
  })

  it('should disable input when streaming', () => {
    const onSend = vi.fn()
    render(<ChatInput onSend={onSend} isStreaming={true} />)

    const input = screen.getByRole('textbox')
    expect(input).toBeDisabled()
  })
})
```

---

## 十、部署架构

### 9.1 开发环境

```
┌─────────────────────────────────────────────────────────────┐
│                      开发环境                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Vite Dev Server)                                │
│  ├─ localhost:5173                                          │
│  ├─ Hot Module Replacement                                  │
│  └─ Proxy /api → localhost:8001                             │
│                                                             │
│  Backend (Uvicorn)                                         │
│  ├─ localhost:8001                                          │
│  ├─ Auto-reload (--reload)                                  │
│  └─ OpenAPI Docs: /docs                                     │
│                                                             │
│  PostgreSQL                                                 │
│  └─ localhost:5432                                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 9.2 生产环境

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                          │
│                   (SSL 终结 + 静态文件)                       │
└────────────────────────────┬────────────────────────────────┘
                             │
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼
┌─────────────────────┐               ┌─────────────────────┐
│   Frontend          │               │  Backend            │
│   (静态文件)         │               │  (Uvicorn + Gunicorn)│
│   Nginx serve       │               │  多 worker 进程      │
└─────────────────────┘               └──────────┬──────────┘
                                                 │
                                        ┌────────▼────────┐
                                        │   PostgreSQL    │
                                        │   (主从复制)     │
                                        └─────────────────┘
```

---

## 十一、总结

### 10.1 项目亮点一览

| 亮点 | 说明 | 面试可深挖 |
|------|------|------------|
| **全异步架构** | FastAPI + AsyncPG + httpx，高并发支持 | 异步原理、性能优化 |
| **多模型支持** | Protocol + Factory 模式，易于扩展 | 设计模式、开放封闭原则 |
| **工具调用** | Agent 循环 + Builder 模式，安全可控 | AI Agent、Function Calling |
| **流式响应** | SSE 实时推送，前端自定义客户端 | HTTP 协议、浏览器 EventSource |
| **安全设计** | API Key 加密、SQL 注入防护 | 加密算法、安全最佳实践 |
| **类型安全** | 全栈 TypeScript + Pydantic | 类型系统、编译时检查 |
| **现代前端** | React 18 + Zustand + Tailwind v4 | 前端工程化、性能优化 |

### 10.2 面试常见问题

1. **为什么选择 FastAPI 而非 Django？**
   - 异步支持、API 优先、类型安全、性能

2. **Agent 循环是如何工作的？**
   - LLM 判断是否需要工具 → 执行工具 → 结果返回 LLM → 循环或输出

3. **SSE 和 WebSocket 的区别？**
   - 单向 vs 双向、HTTP vs WS、自动重连 vs 手动

4. **如何保证 API Key 的安全？**
   - Fernet 加密、PBKDF2 派生密钥、数据库不存明文

5. **前端状态管理为什么选择 Zustand？**
   - 轻量、简单、TypeScript 友好、无 boilerplate

---

> 文档版本: 1.0
> 最后更新: 2026-06-29
> 作者: Claude Code
