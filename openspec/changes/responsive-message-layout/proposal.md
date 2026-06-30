## 为什么

当前消息列表使用 `max-w-3xl mx-auto` 将消息限制在固定宽度并居中显示。这导致在宽屏上消息无法充分利用屏幕空间，用户消息无法真正贴到页面右侧。需要改为响应式布局，让 AI 消息自然靠左、用户消息自然靠右。

## 变更内容

- **移除**：`MessageList.tsx` 中的 `max-w-3xl mx-auto` 居中限制
- **移除**：`ChatInput.tsx` 中的 `max-w-3xl mx-auto` 居中限制
- **添加**：固定边距替代居中布局，确保消息在不同屏幕宽度下都有合适的留白

## 功能 (Capabilities)

### 新增功能

无新增功能。

### 修改功能

- `chat-message-layout`: 修改消息列表和输入框的布局方式，从固定宽度居中改为全宽加固定边距

## 影响

- `frontend/src/components/chat/MessageList.tsx` - 移除 max-w-3xl 居中
- `frontend/src/components/chat/ChatInput.tsx` - 移除 max-w-3xl 居中
- `frontend/src/components/chat/ChatPanel.tsx` - 移除 streaming tool calls 的 max-w-4xl 居中
