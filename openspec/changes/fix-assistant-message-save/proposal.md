## 为什么

历史会话加载时只显示用户消息，不显示大模型回复。根本原因是 FastAPI 流式响应（SSE）与数据库会话生命周期冲突：`StreamingResponse` 返回后，`get_db()` 依赖注入的数据库会话被关闭，导致 `stream_chat_response()` 内部保存 assistant 消息时无法写入数据库。

## 变更内容

- 修复流式响应中 assistant 消息无法保存的问题
- 重构数据库会话管理，确保流式生成期间会话保持活跃

## 功能 (Capabilities)

### 新增功能

（无）

### 修改功能

- `chat-streaming`: 修改流式聊天功能的数据库会话管理方式，确保消息完整保存

## 影响

- `backend/app/api/chat.py` - 需要重构数据库会话的获取和传递方式
- `backend/app/services/message_service.py` - 可能需要支持独立的数据库会话
