## 1. 项目初始化

- [x] 1.1 创建项目根目录结构（frontend/、backend/、docker-compose.yml）
- [x] 1.2 配置 Docker Compose（postgres、backend、frontend 服务）
- [x] 1.3 初始化前端项目（Vite + React + TypeScript）
- [x] 1.4 初始化后端项目（FastAPI + Poetry/requirements.txt）
- [x] 1.5 配置 PostgreSQL 数据库初始化脚本
- [x] 1.6 配置环境变量管理（.env 文件、配置模板）

## 2. 后端数据层

- [x] 2.1 配置 SQLAlchemy 异步引擎和会话
- [x] 2.2 创建数据库模型（GlobalConfig、Session、Message、Provider、ToolCall）
- [x] 2.3 实现 Alembic 数据库迁移
- [x] 2.4 实现 API Key 加密存储工具
- [x] 2.5 初始化全局配置默认数据

## 3. 模型提供者抽象层

- [x] 3.1 定义 ModelProvider 协议/接口
- [x] 3.2 实现 LlamaCppProvider（OpenAI 兼容 API）
- [x] 3.3 实现 OpenAIProvider
- [x] 3.4 实现 CustomProvider（通用 OpenAI 兼容）
- [x] 3.5 实现 Provider 工厂和注册机制
- [x] 3.6 实现模型列表获取 API

## 4. Agent 工具执行层

- [x] 4.1 定义 Tool 协议/接口（name、description、parameters、execute）
- [x] 4.2 实现 ToolExecutor（工具注册、白名单检查、执行调度、超时控制）
- [x] 4.3 实现 WebSearchTool（DuckDuckGo 集成，30秒超时）
- [x] 4.4 实现 DbQueryTool（只读 SQL，表白名单，10秒超时，100行限制）
- [x] 4.5 实现 Function Calling 消息格式适配（OpenAI 格式）
- [x] 4.6 实现工具调用循环（模型 → 工具调用 → 执行 → 结果返回 → 模型继续）

## 5. 后端 API 路由

- [x] 5.1 实现会话管理 API（CRUD，含工具配置）
- [x] 5.2 实现消息管理 API
- [x] 5.3 实现聊天 API（POST /chat，SSE 流式响应，支持 Agent 事件）
- [x] 5.4 实现提供者配置 API
- [x] 5.5 实现全局配置 API（默认参数、系统提示词、表白名单）
- [x] 5.6 实现健康检查 API
- [x] 5.7 配置 CORS 中间件

## 6. 前端基础架构

- [x] 6.1 配置 TailwindCSS
- [x] 6.2 创建基础布局组件（侧边栏、主内容区）
- [x] 6.3 配置 Zustand 状态管理（会话 store、配置 store）
- [x] 6.4 实现 API 客户端（ky/fetch 封装）
- [x] 6.5 实现 SSE 客户端工具（支持多事件类型）

## 7. 聊天界面

- [x] 7.1 创建消息气泡组件（用户/助手区分）
- [x] 7.2 实现聊天输入框组件（多行支持、快捷键）
- [x] 7.3 实现 Markdown 渲染（react-markdown + remark-gfm）
- [x] 7.4 实现代码高亮（react-syntax-highlighter）
- [x] 7.5 实现消息复制功能
- [x] 7.6 实现流式输出显示
- [x] 7.7 实现停止生成按钮

## 8. 会话管理

- [x] 8.1 创建会话列表组件
- [x] 8.2 实现新建会话功能
- [x] 8.3 实现会话切换功能
- [x] 8.4 实现会话删除功能（含确认对话框）
- [x] 8.5 实现会话重命名功能（100字符限制）
- [x] 8.6 实现会话标题自动生成
- [x] 8.7 实现会话级参数配置（temperature、max_tokens、system_prompt）

## 9. 配置管理

- [x] 9.1 创建提供者配置表单组件
- [x] 9.2 实现添加/编辑/删除提供者功能
- [x] 9.3 实现模型选择器组件
- [x] 9.4 实现全局参数配置（默认 temperature、max_tokens）
- [x] 9.5 实现默认系统提示词配置
- [x] 9.6 实现配置验证（API 连接测试）

## 10. Agent 前端集成

- [x] 10.1 创建工具调用卡片组件（显示工具名、参数、状态）
- [x] 10.2 实现工具执行中/成功/失败/超时状态显示
- [x] 10.3 实现工具结果详情展开/折叠
- [x] 10.4 创建会话工具设置组件（工具开关列表）
- [x] 10.5 实现会话工具配置持久化

## 11. 集成与部署

- [x] 11.1 配置前端 Dockerfile（多阶段构建）
- [x] 11.2 配置后端 Dockerfile
- [x] 11.3 完善 docker-compose.yml 环境变量配置
- [x] 11.4 编写 README 部署文档
- [x] 11.5 端到端功能验证

## 12. 测试

- [x] 12.1 后端单元测试（ModelProvider、ToolExecutor）
- [x] 12.2 后端 API 集成测试
- [x] 12.3 前端组件测试（关键组件）
- [x] 12.4 Agent 工具测试（WebSearchTool、DbQueryTool 安全限制验证）
