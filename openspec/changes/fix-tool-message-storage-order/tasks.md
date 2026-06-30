## 1. 后端修改

- [x] 1.1 在 `backend/app/api/chat.py` 中，当 LLM 返回 tool_calls 时，先存储包含 tool_calls 的 assistant 消息
- [x] 1.2 修改 tool 消息存储逻辑，确保在 assistant(tool_calls) 之后存储
- [x] 1.3 最后存储最终的 assistant(response) 消息

## 2. 前端修改

- [x] 2.1 修改 `frontend/src/components/chat/MessageList.tsx`，过滤 `role="tool"` 的消息

## 3. 测试验证

- [x] 3.1 测试工具调用后消息显示不重复
- [x] 3.2 测试工具调用后继续对话不报错
