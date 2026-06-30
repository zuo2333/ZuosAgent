## 上下文

当前 SessionSettings 以右侧固定面板形式存在，与主聊天区域并列，占用水平空间且视觉风格与 SettingsPage（全屏模态）不一致。用户需要一个更轻量的设置入口，能够快速调整参数而不干扰对话流程。

**现有架构：**
- `SessionSettings.tsx` 作为独立面板组件
- `App.tsx` 中通过 `showSessionSettings` 状态控制面板显示
- 面板宽度固定 384px，从右侧滑出

## 目标 / 非目标

**目标：**
- 将 SessionSettings 改为从右上角弹出的 popover 形式
- 点击设置图标触发弹出，点击外部自动关闭
- 宽度 ~400px，固定高度 ~500px + 内部滚动
- 单页分区布局（模型选择 / 参数调整 / 工具设置）
- 与 SettingsPage 视觉风格统一

**非目标：**
- 不改变设置项本身（temperature、max_tokens、system_prompt、tools）
- 不添加新的设置项
- 不改变保存逻辑

## 决策

### 1. Popover 实现方式

**选择：自定义 React 组件 + useRef + useEffect 监听点击外部**

考虑方案：
- A. 使用 Radix UI Popover：功能完善但引入新依赖
- B. 使用 CSS position: absolute + 原生点击检测：轻量，无需依赖

**理由：** 选择方案 B，项目已有多处自定义弹出组件，保持一致性且无需额外依赖。

### 2. 定位策略

**选择：相对于设置按钮定位，右上角对齐**

```
┌────────────────────────────────────┐
│                          [⚙️] ← 触发按钮
│                    ┌───────────────▼───────┐
│                    │   Popover Panel       │
│                    │   (right: 0, top: 8px)│
│                    └───────────────────────┘
└────────────────────────────────────┘
```

### 3. 样式复用

**选择：复用 SettingsPage 的 CSS 变量和圆角/阴影样式**

- 圆角：`rounded-2xl` (16px)
- 阴影：`box-shadow: 0px 8px 12px 0px rgba(0, 0, 0, 0.08)`
- 背景：`var(--token-main-surface-primary)`
- 边框：`1px solid var(--token-border-light)`

### 4. 标题栏样式

**选择：与 SettingsPage Section Header 保持一致**

```tsx
// 标题栏样式
padding: '1.25rem 1.25rem 1rem'
borderBottom: '1px solid var(--token-border-light)'
fontSize: '1rem', fontWeight: 600, color: 'var(--token-text-primary)'
```

标题栏包含：标题文字 + 关闭按钮（右侧）

### 5. ToolSettings 样式适配

**选择：修改 ToolSettings 使用 CSS 变量**

将硬编码颜色替换为 CSS 变量：
- `text-gray-900` → `var(--token-text-primary)`
- `border-gray-200` → `var(--token-border-light)`
- `bg-white` / `bg-gray-50` → `var(--token-main-surface-primary)` / `var(--token-surface-hover)`

### 6. 小屏幕适配

**选择：响应式宽度和动态高度**

- 宽度：`min(400px, calc(100vw - 32px))`
- 最大高度：`calc(100vh - 80px)`
- 面板始终保持在视口内

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 小屏幕上弹出面板可能被截断 | 设置 max-height: calc(100vh - 80px) |
| 点击外部关闭时未保存更改 | 提示用户有未保存的更改 |
| 设置按钮位置变化影响定位 | 使用 ref 动态计算位置 |
