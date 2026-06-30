## 为什么

当前前端 UI 虽然已经进行了一次现代化改造，但与参考的 ChatGPT 风格仍有显著差距。用户要求全面复制 ChatGPT 的 UI 风格，实现真正一致的设计语言。

主要差距：
- 输入框圆角不够大（当前 24px，ChatGPT 为 28px）
- 使用了玻璃模糊效果，ChatGPT 使用纯色背景
- 侧边栏样式不一致（有 Logo 区，ChatGPT 无）
- 设计变量系统不同（color-* vs token-*）
- 欢迎界面样式差异大
- 整体风格仍偏向"渐变+阴影"装饰，不够简洁

## 变更内容

- **输入框重构**：圆角改为 28px，移除渐变阴影，使用纯色细边框
- **侧边栏简化**：移除独立 Logo 区域，简化新建按钮样式，会话项无边框
- **背景纯色化**：移除所有玻璃模糊效果，使用纯色背景
- **设计变量重构**：引入 token-* 变量系统
- **欢迎界面重设计**：大标题居中，移除图标
- **按钮样式简化**：移除渐变，使用纯色
- **消息气泡简化**：移除复杂渐变，使用纯色背景

## 功能 (Capabilities)

### 新增功能

无新增功能。此变更仅涉及 UI 视觉风格调整。

### 修改功能

- `ui-design-system`: 前端设计系统需要全面重构以匹配 ChatGPT 风格

## 影响

- **代码**：
  - `frontend/src/index.css` - 全部 CSS 变量重构
  - `frontend/src/components/layout/AppLayout.tsx` - 移除玻璃效果
  - `frontend/src/components/layout/Sidebar.tsx` - 简化布局，移除 Logo 区
  - `frontend/src/components/chat/ChatInput.tsx` - 圆角 28px，简化样式
  - `frontend/src/components/chat/MessageBubble.tsx` - 简化样式
  - `frontend/src/components/chat/MessageList.tsx` - 欢迎界面重设计
  - `frontend/src/components/session/SessionList.tsx` - 简化会话项样式
- **依赖项**：无新增依赖
- **向后兼容**：纯样式变更，不影响功能逻辑
