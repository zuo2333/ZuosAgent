## 上下文

当前工具调用展示架构：

```
ChatPanel
├── MessageList (消息流)
│   ├── User Message
│   └── Assistant Message (完成后才包含 tool_calls)
├── StreamingToolCalls (临时区域) ← 工具调用时在此展示
└── ChatInput
```

问题：工具调用完成后，`StreamingToolCalls` 清空，`assistantMessage` 添加到消息流，导致工具卡片从底部"跳"到消息流中。

## 目标 / 非目标

**目标：**
- 工具调用从开始到完成都在消息流中的同一位置展示
- 状态转变（running → success）在原地平滑过渡
- 最小化代码改动，复用现有组件

**非目标：**
- 不改变工具调用的数据结构和事件流
- 不改变工具卡片的视觉样式

## 决策

### 决策 1：将 StreamingToolCalls 移入 MessageList

**选择方案**: MessageList 接收 `streamingToolCalls` prop，在消息末尾渲染

**替代方案**:
- 方案 B：创建"占位工具消息"到 messages 数组 - 放弃，需要修改 Message 类型，改动较大
- 方案 C：保持现状但添加动画过渡 - 放弃，仍有视觉跳动

**理由**: 方案 A 改动最小，只需修改两个组件的 props 传递，无需修改数据类型。

### 决策 2：展示时机

**选择**: 当 `isStreaming && streamingToolCalls.length > 0` 时在消息流末尾展示

**理由**: 与现有逻辑一致，`StreamingToolCalls` 组件已有完整的状态展示逻辑。

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| MessageList 组件职责增加 | 仅作为展示位置，状态管理仍在 ChatPanel |
| 滚动行为变化 | 保持现有 `scrollIntoView` 逻辑，工具卡片更新时也会触发滚动 |

## 实现概要

```
改动后架构：

ChatPanel
├── MessageList (消息流)
│   ├── User Message
│   ├── StreamingToolCalls ← 移到这里 (isStreaming 时)
│   └── StreamingMessage (AI 内容流式输出)
└── ChatInput

关键改动：
1. MessageList 接收 streamingToolCalls prop
2. MessageList 在消息末尾渲染 StreamingToolCalls
3. ChatPanel 移除底部独立的 StreamingToolCalls 展示
```
