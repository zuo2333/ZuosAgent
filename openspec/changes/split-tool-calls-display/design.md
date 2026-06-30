## 上下文

当前 `MessageBubble` 组件直接渲染 `message.tool_calls` 数组，所有工具调用在同一条消息内显示，共享一个 AI Avatar。用户希望每个工具调用作为独立的消息块显示，每个都有自己的 Avatar。

## 目标 / 非目标

**目标：**
- 每个 tool_call 作为独立的消息块渲染，带有独立的 AI Avatar
- 视觉效果统一：无论一条消息包含几个 tool_calls，都显示为多个独立的消息

**非目标：**
- 不修改后端存储逻辑
- 不修改数据库结构

## 决策

### 决策 1：前端拆分渲染，每个工具调用独立显示

**选择方案：** 在 `MessageBubble` 组件中，将每个 `tool_call` 渲染为独立的消息块，每个都有自己的 AI Avatar

**视觉效果：**
```
修改前（多个工具调用共享 Avatar）：
┌────────┐
│ Avatar │  ToolCallCard 1
│   ⚡   │  ToolCallCard 2
│        │  Markdown内容
└────────┘

修改后（每个工具调用独立 Avatar）：
┌────────┐
│ Avatar │  ToolCallCard 1
│   ⚡   │
└────────┘

┌────────┐
│ Avatar │  ToolCallCard 2
│   ⚡   │
└────────┘

┌────────┐
│ Avatar │  Markdown内容
│   ⚡   │
└────────┘
```

**实现方式：**

```tsx
// MessageBubble.tsx
function MessageBubble({ message }) {
  const hasToolCalls = message.tool_calls && message.tool_calls.length > 0

  // 如果有工具调用，拆分为多个独立的消息块
  if (hasToolCalls) {
    return (
      <>
        {/* 每个工具调用作为独立消息 */}
        {message.tool_calls.map((tc, index) => (
          <div key={tc.id} className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]">
            <div className="flex items-center" style={{ gap: '12px' }}>
              {/* AI Avatar - 每个工具调用都有 */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                style={{ background: 'var(--token-surface-tertiary)', color: 'var(--token-text-secondary)' }}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="flex-1 flex flex-col gap-2 min-w-0">
                <ToolCallCard toolCall={tc} />
              </div>
            </div>
          </div>
        ))}
        
        {/* 文本内容作为独立消息 */}
        {message.content && (
          <div className="flex flex-col w-full justify-start animate-fade-in-up max-w-[70%]">
            <div className="flex items-center" style={{ gap: '12px' }}>
              {/* AI Avatar */}
              <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium"
                style={{ background: 'var(--token-surface-tertiary)', color: 'var(--token-text-secondary)' }}>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <div className="flex-1 flex flex-col gap-2 min-w-0">
                <MarkdownRenderer content={message.content} />
              </div>
            </div>
          </div>
        )}
      </>
    )
  }

  // 普通消息渲染...
}
```

**理由：**
- 视觉效果统一：每个工具调用看起来像独立的消息
- 符合用户直觉：每个"动作"有自己的标识
- 改动仅在前端，不影响后端

## 风险 / 权衡

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 消息数量变化 | 前端显示的消息数量可能与数据库记录数不一致 | 这是期望的行为，用户看到的是逻辑消息而非存储消息 |
| Avatar 组件重复 | 多个 Avatar 可能导致代码重复 | 可提取为独立的 Avatar 组件复用 |
