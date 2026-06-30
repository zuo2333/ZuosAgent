## 为什么

当前工具调用（如 Web Search）在执行过程中显示在聊天输入框上方的临时区域，但当 AI 回复完成后，这些工具调用记录会"跳动"到消息流中作为 AI 消息的一部分展示。这种位置变化导致视觉不连贯，用户体验不佳。

我们希望工具调用从"开始"到"完成"都在消息流中的同一位置展示，状态原地转变，不再有视觉跳动。

## 变更内容

- **修改**: 将 `StreamingToolCalls` 组件的展示位置从 `ChatPanel` 底部移到 `MessageList` 消息流末尾
- **修改**: `MessageList` 组件新增 `streamingToolCalls` 属性，在消息末尾渲染流式工具调用
- **移除**: `ChatPanel` 中底部独立的 `StreamingToolCalls` 展示区域

## 功能 (Capabilities)

### 新增功能

无新增功能，这是现有工具调用展示逻辑的优化。

### 修改功能

- `streaming-tools-display`: 工具调用展示位置从底部临时区域改为消息流中，确保工具卡片在原地完成状态转变

## 影响

- **前端组件**:
  - `MessageList.tsx`: 新增 `streamingToolCalls` 属性，修改渲染逻辑
  - `ChatPanel.tsx`: 移除底部 `StreamingToolCalls` 展示，传递 prop 给 `MessageList`
- **现有组件复用**: `StreamingToolCalls.tsx` 和 `ToolCallCard.tsx` 组件无需修改，可直接复用
- **用户体验**: 工具调用展示更加连贯，消除视觉跳动
