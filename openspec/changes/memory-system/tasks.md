# 记忆系统实现任务

## 1. 数据库基础设施

- [x] 1.1 启用 PostgreSQL pgvector 扩展
- [x] 1.2 创建 short_term_memories 表迁移
- [x] 1.3 创建 long_term_memories 表迁移（含向量列）
- [x] 1.4 创建 user_profiles 表迁移
- [x] 1.5 创建向量索引（HNSW）
- [ ] 1.6 运行迁移验证

## 2. 数据模型层

- [x] 2.1 创建 ShortTermMemory SQLAlchemy 模型
- [x] 2.2 创建 LongTermMemory SQLAlchemy 模型
- [x] 2.3 创建 UserProfile SQLAlchemy 模型
- [x] 2.4 创建 MemoryType 枚举
- [x] 2.5 创建 Pydantic schema（请求/响应模型）

## 3. Embedding 服务

- [x] 3.1 实现 EmbeddingService 接口
- [x] 3.2 集成 sentence-transformers 本地模型
- [x] 3.3 添加 OpenAI Embedding 备选实现
- [x] 3.4 实现配置切换逻辑
- [x] 3.5 添加缓存机制（可选）

## 4. 短期记忆服务

- [x] 4.1 实现 ShortTermMemoryService 基础 CRUD
- [x] 4.2 实现会话摘要生成（LLM 调用）
- [x] 4.3 实现实体提取逻辑（压缩时批量提取）
- [x] 4.4 实现任务状态跟踪
- [x] 4.5 实现 Token 统计和压缩触发
- [x] 4.6 实现滑动窗口压缩逻辑
- [x] 4.7 实现一次性 LLM 调用（摘要 + 实体 + 任务）

## 5. 长期记忆服务

- [x] 5.1 实现 LongTermMemoryService 基础 CRUD
- [x] 5.2 实现记忆提取 LLM Pipeline
- [x] 5.3 实现向量嵌入生成
- [x] 5.4 实现向量相似度检索
- [x] 5.5 实现记忆去重逻辑
- [x] 5.6 实现重要性评分更新
- [x] 5.7 实现访问统计更新
- [x] 5.8 实现遗忘曲线衰减
- [x] 5.9 实现会话结束检测（闲置检测、切换检测）
- [x] 5.10 实现定期检查点触发（每 20 条消息）

## 6. 用户画像服务

- [x] 6.1 实现 UserProfileService 基础 CRUD
- [x] 6.2 实现行为特征自动更新
- [x] 6.3 实现画像推断 LLM Pipeline
- [x] 6.4 实现知识图谱更新逻辑
- [x] 6.5 实现推断频率控制

## 7. 记忆上下文整合

- [x] 7.1 实现 MemoryContextService
- [x] 7.2 实现用户画像格式化
- [x] 7.3 实现长期记忆检索和格式化
- [x] 7.4 实现短期记忆格式化
- [x] 7.5 实现 Token 预算控制
- [x] 7.6 实现 System Prompt 模板渲染
- [x] 7.7 实现记忆意图分类器（规则匹配，无 LLM）
- [x] 7.8 实现按需记忆注入逻辑

## 8. Agent 循环集成

- [x] 8.1 修改 chat API 集成意图分类器
- [x] 8.2 实现按需记忆上下文注入
- [x] 8.3 实现会话结束时的记忆提取触发
- [x] 8.4 实现检查点触发（每 20 条消息）
- [x] 8.5 添加记忆提取配置开关
- [x] 8.6 添加记忆功能开关

## 9. API 端点

- [x] 9.1 创建 memory_router（记忆管理 API）
- [x] 9.2 实现 POST /api/memory/extract 端点
- [x] 9.3 实现 GET /api/memory/search 端点
- [x] 9.4 实现 DELETE /api/memory/{id} 端点
- [x] 9.5 实现 GET /api/memory/stats 端点
- [x] 9.6 创建 profile_router（用户画像 API）
- [x] 9.7 实现 GET /api/profile 端点
- [x] 9.8 实现 PATCH /api/profile 端点
- [x] 9.9 实现 POST /api/profile/infer 端点
- [x] 9.10 注册路由到 main.py

## 10. 测试

- [x] 10.1 编写 ShortTermMemoryService 单元测试
- [x] 10.2 编写 LongTermMemoryService 单元测试
- [x] 10.3 编写 UserProfileService 单元测试
- [x] 10.4 编写 EmbeddingService 单元测试
- [x] 10.5 编写 MemoryIntentClassifier 单元测试
- [x] 10.6 编写 Memory API 集成测试
- [x] 10.7 编写 Profile API 集成测试
- [x] 10.8 编写意图分类集成测试（各场景验证）

## 11. 文档与配置

- [x] 11.1 更新 requirements.txt 添加新依赖
- [x] 11.2 更新配置文件添加记忆相关配置项
- [x] 11.3 更新技术文档（docs/TECHNICAL_OVERVIEW.md）
- [x] 11.4 添加记忆意图分类规则文档
