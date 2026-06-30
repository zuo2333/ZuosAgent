## 1. 前端修改

- [ ] 1.1 提取 AI Avatar 为独立组件（可选，减少代码重复）
- [ ] 1.2 修改 `frontend/src/components/chat/MessageBubble.tsx`，将多个 tool_calls 拆分为独立的消息块
- [ ] 1.3 每个消息块都有独立的 AI Avatar
- [ ] 1.4 确保消息块之间有适当的间距

## 2. 测试验证

- [ ] 2.1 测试单个工具调用显示正确（带 Avatar）
- [ ] 2.2 测试多个工具调用独立显示（每个带 Avatar）
- [ ] 2.3 测试工具调用加文本内容的显示（各带 Avatar）
