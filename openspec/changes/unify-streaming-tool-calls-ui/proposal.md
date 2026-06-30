## 为什么

当前存在两个工具调用展示组件（`StreamingToolCalls.tsx` 和 `ToolCallCard.tsx`），它们的视觉风格完全不同：
- StreamingToolCalls 使用彩色背景（蓝/绿/红）+ 粗边框 + Emoji 图标
- ToolCallCard 使用白色背景 + 浅灰边框 + SVG 图标 + 状态徽章

这种不一致导致用户在工具执行过程中和执行完成后看到截然不同的 UI，造成视觉断层和困惑。

## 变更内容

重构 `StreamingToolCalls.tsx` 组件，使其与 `ToolCallCard.tsx` 保持一致的设计语言：
- 统一使用白色背景 + 浅灰边框
- 统一使用 SVG 图标替代 Emoji
- 统一状态徽章样式（小圆点 + 文字标签）
- 参数展示改为行内 `key="value"` 格式
- 移除假进度条，改用耗时计时 + 旋转动画
- 多个工具调用堆叠显示，运行中的展开、完成的折叠

## 功能 (Capabilities)

### 新增功能

（无新增功能）

### 修改功能

- `streaming-tool-calls`: 重构工具调用进行中的 UI 组件，统一设计语言

## 影响

- `frontend/src/components/chat/StreamingToolCalls.tsx` - 主要修改文件
- `frontend/src/components/chat/ToolCallCard.tsx` - 参考设计，可能需要微调以共享样式
