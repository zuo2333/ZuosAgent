## 上下文

当前 `MessageBubble.tsx` 组件使用 Flexbox 布局，但存在以下问题：
- 外层容器使用 `flex gap-4`，但 `align-items` 默认为 `stretch`
- 用户消息的 `justify-end` 虽然有 `flex` 属性，但气泡宽度被 `max-w-[85%]` 限制
- 头像 (32px) 与气泡的垂直对齐不一致

## 目标 / 非目标

**目标：**
- 用户消息气泡在 `max-w-3xl` 容器内正确右对齐
- 头像与消息气泡顶部对齐
- AI 消息保持左对齐
- 保持 ChatGPT 风格的居中布局

**非目标：**
- 不改变消息最大宽度 (`max-w-3xl`)
- 不改变气泡内边距和圆角样式
- 不引入新的 CSS 类或依赖

## 决策

### 决策 1: 使用 `items-start` 对齐头像和气泡

**选择**: 在外层容器添加 `items-start`

**理由**: 头像高度固定为 32px，气泡高度随内容变化。使用 `items-start` 确保头像与气泡顶部对齐。

**替代方案**:
- `items-center`: 头像会垂直居中，与短消息对齐差
- `items-end`: 头像在底部，不符合阅读习惯

### 决策 2: 用户消息使用 `ml-auto` 替代 `flex justify-end`

**选择**: 移除 `flex-1` 上的 `flex justify-end`，改用 `ml-auto` 让气泡靠右

**理由**: 更简单直接，避免嵌套 flex 容器的复杂性

**代码变更**:
```jsx
// Before
<div className={`flex-1 ${isUser ? 'flex justify-end' : ''}`}>

// After
<div className={`flex-1 ${isUser ? 'ml-auto' : ''}`}>
```

### 决策 3: 用户消息气泡宽度调整为 90%

**选择**: 用户消息气泡 `max-w` 从 85% 改为 90%，AI 消息保持 85%

**理由**: 用户消息通常是简短的输入，稍宽的气泡让界面更平衡，同时保留适度留白

**代码变更**:
```jsx
// Before
<div className={`relative max-w-[85%] group`}>

// After (条件渲染)
<div className={`relative group ${isUser ? 'max-w-[90%]' : 'max-w-[85%]'}`}>
```

## 风险 / 权衡

- **风险**: 改动较小，可能不足以解决所有边界情况
  - **缓解**: 先实现基础修复，后续根据实际效果调整
