## 上下文

当前 `MessageList.tsx` 和 `ChatInput.tsx` 使用 `max-w-3xl mx-auto` 限制宽度并居中。这导致：
- 消息被限制在 768px 宽度内
- 用户消息无法真正贴到页面右侧
- 在宽屏上空间利用率低

## 目标 / 非目标

**目标：**
- 消息列表占满可用宽度
- AI 消息自然靠左对齐
- 用户消息自然靠右对齐
- 保持固定边距确保可读性

**非目标：**
- 不实现 ChatGPT 的容器查询响应式边距
- 不改变气泡的 max-w 百分比
- 不改变头像和气泡的内部布局

## 决策

### 决策 1: MessageList 移除居中，改用固定边距

**选择**: 移除 `max-w-3xl mx-auto`，改用 `w-full px-6`

**理由**: 
- `w-full` 让消息列表占满宽度
- `px-6` (24px) 提供固定左右边距
- 用户消息的 `ml-auto` 会自然将气泡推到右侧

**代码变更**:
```jsx
// MessageList.tsx Before
<div className="max-w-3xl mx-auto space-y-2">

// After
<div className="w-full px-6 space-y-2">
```

### 决策 2: ChatInput 同步移除居中

**选择**: 移除 `max-w-3xl mx-auto`，改用 `w-full px-6`

**理由**: 输入框应与消息列表保持一致的边距

**代码变更**:
```jsx
// ChatInput.tsx Before
<div className="max-w-3xl mx-auto">

// After
<div className="w-full px-6">
```

### 决策 3: ChatPanel 移除 streaming tool calls 的居中

**选择**: 移除 `max-w-4xl mx-auto`，改用 `w-full px-6`

**理由**: streaming tool calls 显示区域应与消息列表保持一致

**代码变更**:
```jsx
// ChatPanel.tsx Before
<div className="px-6 pb-3 max-w-4xl mx-auto w-full">

// After
<div className="px-6 pb-3 w-full">
```

## 风险 / 权衡

- **风险**: 宽屏上消息可能过长影响可读性
  - **缓解**: 气泡已有 `max-w-[85%]/[90%]` 限制，不会占满整行

### 决策 4: 用户消息气泡样式优化

**选择**:
- 移除 `max-w-[90%]`，让气泡宽度自适应内容
- 气泡颜色从黑色改为浅灰色
- 减小头像与气泡间距 (gap-4 → gap-2)
- 气泡内文字居中

**理由**: 用户消息通常是简短输入，气泡应紧凑显示，不需要占满宽度

**代码变更**:
```jsx
// MessageBubble.tsx Before
<div className={`flex gap-4 mb-4 items-start animate-fade-in-up ${isUser ? 'flex-row-reverse' : ''}`}>
  ...
  <div className={`flex-1 ${isUser ? 'ml-auto' : ''}`}>
    <div className={`relative group ${isUser ? 'max-w-[90%]' : 'max-w-[85%]'}`}>
      <div className={`px-4 py-3 ...`} style={isUser ? { background: 'var(--token-text-primary)', ... } : ...}>

// After
<div className={`flex gap-2 mb-4 items-start animate-fade-in-up ${isUser ? 'flex-row-reverse' : ''}`}>
  ...
  <div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>
    <div className={`relative group ${isUser ? '' : 'max-w-[85%]'}`}>
      <div className={`px-4 py-3 text-center ...`} style={isUser ? { background: 'var(--token-surface-tertiary)', color: 'var(--token-text-primary)' } : ...}>
```
