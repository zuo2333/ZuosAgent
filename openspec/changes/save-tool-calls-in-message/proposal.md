## 为什么

历史会话中的工具调用记录（如 Web Search、Database Query）在重新打开会话后消失。原因是后端保存 assistant 消息时只保存了 `content` 字段，没有保存 `tool_calls` 字段到数据库，导致历史加载时无法恢复工具调用卡片。

## 变更内容

- 修改 `stream_chat_response` 函数，在保存 assistant 消息时同时保存 `tool_calls` 数据
- 确保工具调用的名称、参数、状态、结果等信息完整持久化

## 功能 (Capabilities)

### 新增功能

（无）

### 修改功能

- `chat-streaming`: 修改消息保存逻辑，将工具调用记录一并保存到数据库的 `tool_calls` 字段

## 影响

- `backend/app/api/chat.py` - 修改 `stream_chat_response` 中保存消息的逻辑
- 消息类型 `Message.tool_calls` 格式需要与前端 `ToolCallCard` 组件兼容
