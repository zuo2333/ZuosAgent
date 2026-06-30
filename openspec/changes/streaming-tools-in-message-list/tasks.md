## 1. MessageList 组件修改

- [x] 1.1 MessageList 接口新增 streamingToolCalls 可选属性
- [x] 1.2 MessageList 在消息末尾渲染 StreamingToolCalls 组件
- [x] 1.3 添加滚动触发逻辑，确保工具卡片更新时滚动到底部

## 2. ChatPanel 组件修改

- [x] 2.1 移除 ChatPanel 底部独立的 StreamingToolCalls 展示区域
- [x] 2.2 将 streamingToolCalls 和 isStreaming 状态传递给 MessageList 组件

## 3. 验证测试

- [x] 3.1 测试工具调用开始时卡片在消息流中展示
- [x] 3.2 测试工具状态从 running 变为 success 时原地转变
- [x] 3.3 测试多个工具调用顺序展示
- [x] 3.4 测试 AI 回复追加在工具卡片下方
