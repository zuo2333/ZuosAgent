## 为什么

当前工具调用消息的存储顺序错误：`tool` 角色的消息在 `assistant` 消息之前存储，导致两个严重问题：

1. **继续对话时报错**：OpenAI 兼容 API 要求 `tool` 消息必须紧跟在包含 `tool_calls` 的 `assistant` 消息之后，否则返回 400 错误
2. **消息重复显示**：前端未过滤 `tool` 角色消息，导致工具结果在界面上显示两次（一次作为 tool 消息，一次通过 assistant.tool_calls 渲染）

这是一个影响核心聊天功能的 bug，需要立即修复。

## 变更内容

- **修复消息存储顺序**：在 `chat.py` 中，先存储包含 `tool_calls` 的 `assistant` 消息，再存储 `tool` 消息
- **前端过滤 tool 消息**：在 `MessageList.tsx` 中过滤掉 `role="tool"` 的消息，因为工具调用信息已通过 `assistant.tool_calls` 渲染
- **优化消息存储逻辑**：将工具消息存储移到最终的 assistant 消息保存之后，确保正确的消息顺序

## 功能 (Capabilities)

### 新增功能

无

### 修改功能

- `chat-message-storage`: 修改消息存储顺序，确保 tool 消息始终在对应的 assistant 消息之后

## 影响

- **后端**：`backend/app/api/chat.py` - 修改 `stream_chat_response` 函数的消息存储逻辑
- **前端**：`frontend/src/components/chat/MessageList.tsx` - 过滤 tool 角色消息
- **数据库**：现有数据不受影响（只是存储顺序变更），但已存储的错误顺序数据可能需要考虑迁移或容忍
- **API**：无接口变更，对用户透明
