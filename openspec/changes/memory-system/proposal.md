# 记忆系统 (Memory System)

## 为什么

当前 AI 助手每次对话都是"新"的，无法记住用户的偏好、历史重要信息和之前的对话上下文。这导致：

1. **重复说明**：用户每次都要重新介绍背景信息
2. **缺乏个性化**：AI 无法根据用户习惯调整回复风格
3. **上下文断裂**：跨会话的任务无法延续

现在是实现记忆系统的最佳时机，因为项目已有完整的工具调用架构和会话管理基础，记忆系统可以自然地融入现有 Agent 循环。

## 变更内容

### 新增功能

- **短期记忆 (Working Memory)**：当前会话的工作记忆，包括会话摘要、关键实体提取、当前任务状态跟踪
- **长期记忆 (Long-term Memory)**：跨会话的知识持久化，使用向量数据库存储，支持语义检索
- **用户画像 (User Profile)**：全局用户认知，存储用户偏好、行为特征、知识图谱

### 技术变更

- 新增 PostgreSQL 表：`short_term_memories`、`long_term_memories`、`user_profiles`
- 集成 pgvector 扩展用于向量存储和检索
- 新增记忆服务层：`MemoryService`、`ProfileService`
- 修改 Agent 循环，在 LLM 调用前注入记忆上下文
- 新增 API 端点用于记忆管理和用户画像配置

## 功能 (Capabilities)

### 新增功能

- `short-term-memory`: 当前会话的摘要生成、实体提取、任务状态跟踪，支持滑动窗口压缩
- `long-term-memory`: 基于向量数据库的知识持久化存储，支持记忆提取、检索、遗忘曲线
- `user-profile`: 用户偏好设置、行为特征分析、知识图谱构建

### 修改功能

- `chat`: 在 LLM 调用前注入记忆上下文到 System Prompt，增强回复的个性化
- `sessions`: 会话结束时触发记忆提取和存储，更新用户画像

## 影响

### 数据库

- 新增 `short_term_memories` 表（关联 sessions）
- 新增 `long_term_memories` 表（支持向量索引）
- 新增 `user_profiles` 表
- 启用 PostgreSQL pgvector 扩展

### API

- `POST /api/memory/extract` - 手动触发记忆提取
- `GET /api/memory/search` - 搜索长期记忆
- `GET /api/profile` - 获取用户画像
- `PATCH /api/profile` - 更新用户画像

### 依赖

- 新增 Python 依赖：`pgvector`（向量操作）
- 可选：`sentence-transformers`（本地 Embedding 模型）

### 兼容性

- 无破坏性变更
- 现有会话自动获得短期记忆支持
- 长期记忆需要用户重新开始对话后逐步积累
