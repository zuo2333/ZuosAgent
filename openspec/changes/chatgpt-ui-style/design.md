## 上下文

当前前端 UI 经过一次现代化改造，但仍未达到 ChatGPT 的设计水准。经过深入分析 sample.html，发现以下关键差距：

**布局结构差距：**
- 缺少 sticky Header 组件
- Composer 输入框未使用 Grid 布局
- 侧边栏结构不完整（缺少 rail、底部区域）
- 输入框缺少左侧 + 按钮
- 会话项交互细节不正确
- 新建按钮样式不正确

目标：全面复制 ChatGPT 的布局结构和设计风格。

## 目标 / 非目标

**目标：**
- 添加 sticky Header 组件（h-header-height）
- Composer 使用 CSS Grid 布局（3列结构）
- 输入框圆角 28px，左侧有 + 按钮
- 侧边栏使用 --sidebar-width 变量，底部有登录区域
- 会话项使用 group/__menu-item 样式
- 新建按钮使用菜单项样式（非文字链接）
- 移除所有玻璃模糊效果
- 引入 token-* 设计变量系统

**非目标：**
- 不添加新功能（模型切换、语音输入等）
- 不修改后端 API
- 不添加新依赖
- 不实现暗色模式
- 不实现 sidebar rail 拖拽调整宽度

## 决策

### 1. 布局变量系统

**选择**：引入 ChatGPT 的布局变量

```css
:root {
  --sidebar-width: 260px;
  --header-height: 52px;
  --composer-min-height: 52px;
}
```

**理由**：与 ChatGPT 布局尺寸一致

### 2. Header 组件

**选择**：添加 sticky Header

```tsx
<header className="sticky top-0 z-20 flex items-center justify-between"
  style={{
    height: 'var(--header-height)',
    padding: '0.5rem 1rem',
    background: 'var(--token-surface-primary)',
  }}>
  {/* 左侧：菜单按钮 */}
  {/* 中间：会话标题 */}
  {/* 右侧：操作按钮 */}
</header>
```

**理由**：ChatGPT 有固定的顶部 Header，包含菜单和操作按钮

### 3. Composer (输入框) Grid 布局

**选择**：使用 CSS Grid 三列布局

```css
.composer-container {
  display: grid;
  grid-template-columns: auto 1fr auto;
  grid-template-areas:
    'leading primary trailing';
  min-height: 52px;
  padding: 9px 8px;
  border-radius: 28px;
  background: var(--token-surface-primary);
  border: 1px solid var(--token-border-light);
  box-shadow: var(--shadow-short-composer);
}

.leading { grid-area: leading; }   /* 左侧 + 按钮 */
.primary { grid-area: primary; }   /* 中间输入区 */
.trailing { grid-area: trailing; } /* 右侧发送按钮 */
```

**理由**：ChatGPT 使用 Grid 布局组织输入框内部元素

### 4. 输入框左侧按钮

**选择**：添加左侧 + 按钮

```tsx
<button className="flex items-center justify-center rounded-full"
  style={{ width: '36px', height: '36px' }}>
  <svg><!-- plus icon --></svg>
</button>
```

**理由**：ChatGPT 输入框左侧有附加功能按钮

### 5. 侧边栏结构

**选择**：完整侧边栏结构

```tsx
<aside style={{ width: 'var(--sidebar-width)' }}>
  {/* 顶部区域：新建按钮 */}
  <div className="p-2">
    <button className="group __menu-item hoverable gap-1.5">
      <span className="icon"><!-- plus icon --></span>
      <span>新对话</span>
    </button>
  </div>
  
  {/* 会话列表 */}
  <nav className="flex-1 overflow-y-auto">
    {/* 会话项 */}
  </nav>
  
  {/* 底部区域：登录/设置 */}
  <div className="sticky bottom-0 p-5 border-t">
    {/* 登录或用户信息 */}
  </div>
</aside>
```

**理由**：ChatGPT 侧边栏有三部分：顶部操作、中间列表、底部区域

### 6. 会话项样式

**选择**：使用 group/__menu-item 样式

```tsx
<div className="group __menu-item hoverable flex items-center gap-1.5 px-2 py-1.5 rounded-lg cursor-pointer">
  <span className="icon flex items-center justify-center w-6 h-6">
    {/* 消息图标 */}
  </span>
  <span className="flex-1 truncate text-sm">
    {session.title}
  </span>
  {/* hover 时显示操作按钮 */}
</div>
```

**理由**：ChatGPT 会话项使用这种结构，hover 时有背景变化

### 7. 新建按钮样式

**选择**：菜单项样式（非文字链接）

```tsx
<button className="group __menu-item hoverable gap-1.5 flex items-center w-full px-3 py-2 rounded-lg">
  <span className="icon w-6 h-6 flex items-center justify-center">
    <svg><!-- plus icon --></svg>
  </span>
  <span className="text-sm font-medium">新对话</span>
</button>
```

**理由**：ChatGPT 新建按钮是带图标的菜单项样式，不是纯文字链接

### 8. 设计变量系统

**选择**：引入 token-* 变量系统

```css
:root {
  --token-text-primary: #0d0d0d;
  --token-text-secondary: #6b6b6b;
  --token-text-tertiary: #9b9b9b;
  --token-surface-primary: #ffffff;
  --token-surface-secondary: #f7f7f7;
  --token-border-light: #e5e5e5;
  --token-border-heavy: #d9d9d9;
  --shadow-short-composer: 0 0 0 1px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.05);
}
```

**理由**：与 ChatGPT 设计语言一致

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 新增 Header 组件需要调整布局 | 使用 sticky 定位，不影响滚动 |
| Grid 布局可能需要调整响应式 | 设置合理的 min-height |
| 左侧按钮功能未实现 | 保留按钮占位，后续可扩展 |

## 实现文件清单

| 文件 | 修改内容 |
|------|----------|
| `frontend/src/index.css` | 引入 token-* 变量、布局变量 |
| `frontend/src/components/layout/AppLayout.tsx` | 调整布局结构 |
| `frontend/src/components/layout/Sidebar.tsx` | 重构侧边栏结构 |
| `frontend/src/components/layout/Header.tsx` | **新建** Header 组件 |
| `frontend/src/components/chat/ChatInput.tsx` | Grid 布局、左侧按钮 |
| `frontend/src/components/chat/MessageBubble.tsx` | 简化样式 |
| `frontend/src/components/chat/MessageList.tsx` | 欢迎界面重设计 |
| `frontend/src/components/session/SessionList.tsx` | 会话项样式重构 |
