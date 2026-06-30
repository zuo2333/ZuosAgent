## 为什么

当前消息存储存在两个问题：

1. **tool_calls 累积问题**：最终 assistant 消息错误地包含了所有历史工具调用，导致 OpenAI API 报错：
   ```
   Message format error, index[10] should be [tool] but is [user]
   ```

2. **数据冗余问题**：工具执行结果同时存储在 tool 消息和 assistant.tool_calls 中，违反数据分离原则

**问题根源**：
- `saved_tool_calls` 变量在循环外部定义，累积所有迭代
- 数据存储未遵循 OpenAI 消息格式规范

**影响**：
1. 多轮工具调用后继续对话会报 400 错误
2. 数据冗余，难以维护

## 变更内容

- **移除累积变量**：`saved_tool_calls` 改为每轮独立的 `iteration_tool_calls`
- **每轮独立存储**：assistant(tool_calls) 包含当前轮次的完整信息（含 result），不累积历史
- **最终消息无 tool_calls**：最终 assistant 响应的 tool_calls 为 null
- **符合 OpenAI 规范**：消息顺序正确，API 不报错

## 功能 (Capabilities)

### 新增功能

无

### 修改功能

- `chat-message-storage`: 修改消息存储逻辑，每轮独立存储，不累积历史

## 影响

- **后端**：`backend/app/api/chat.py` - 修改 `stream_chat_response` 函数
- **前端**：无需修改（前端从 assistant.tool_calls 直接获取完整信息）
- **数据库**：现有错误数据可清理（可选）
