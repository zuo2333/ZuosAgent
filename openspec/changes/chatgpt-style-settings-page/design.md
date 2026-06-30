## 上下文

当前 `SettingsPage.tsx` 使用水平标签页布局，需要重构为 ChatGPT 风格的垂直左侧导航 + 右侧内容区布局。ChatGPT 设置页面的关键特征：
- 左侧导航栏 180-210px 宽度
- 右侧内容区可滚动
- 导航项带图标，使用圆角背景高亮活跃状态
- 移动端导航变为水平滚动

## 目标 / 非目标

**目标：**
- 实现 ChatGPT 风格的左右分栏布局
- 左侧垂直导航栏带图标和活跃状态高亮
- 响应式设计：移动端导航水平滚动
- 保持现有功能不变（Providers、Defaults 两个标签页）

**非目标：**
- 不增加新的设置项
- 不改变后端 API
- 不实现暗色模式

## 决策

### 决策 1：布局结构

**选择**：使用 Flexbox 实现左右分栏，移动端使用 `flex-col` 切换为上下布局。

**理由**：
- 与 ChatGPT 一致的响应式策略
- 简单直接，无需额外库

**布局尺寸**：
```
┌─────────────────────────────────────────┐
│ 容器: max-w-[680px], h-[420px]          │
├───────────────┬─────────────────────────┤
│ 导航栏        │ 内容区                   │
│ 180-210px     │ flex-1                   │
│               │                          │
│ [X] 关闭      │ Section 标题             │
│               │ ─────────────────────── │
│ [🔧] 常规     │ 设置项列表               │
│ [📊] 数据管理  │                          │
│               │                          │
└───────────────┴─────────────────────────┘
```

### 决策 2：导航项样式

**选择**：复用 `index.css` 中已有的 `__menu-item` 样式类。

**样式定义**：
```css
.__menu-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  gap: 0.375rem; /* gap-1.5 */
}
.__menu-item.hoverable:hover {
  background: var(--token-surface-tertiary);
}
```

**活跃状态**：通过 `data-[state=active]` 或条件样式设置背景色为 `var(--token-surface-tertiary)`。

### 决策 3：移动端响应式

**选择**：使用 Tailwind 的 `md:` 断点实现响应式。

**行为**：
- 桌面端（md+）：左右分栏，导航栏垂直
- 移动端（<md）：上下布局，导航栏水平滚动，边框在底部而非右侧

### 决策 4：ARIA 无障碍属性

**选择**：遵循 ChatGPT 的 ARIA 实现，使用 Radix UI 风格的属性。

**属性定义**：
- 容器：`role="dialog"`, `aria-modal="true"`, `data-state="open"`
- 导航栏：`role="tablist"`, `aria-orientation="vertical"`
- 导航项：`role="tab"`, `aria-selected="{true/false}"`, `data-state="active/inactive"`
- 内容区：`role="tabpanel"`, `aria-labelledby="{tab-id}"`

**理由**：
- 提升无障碍体验
- 与 ChatGPT 保持一致
- 支持屏幕阅读器导航

### 决策 5：导航栏边框与分隔

**选择**：导航栏右侧添加浅色边框作为视觉分隔。

**样式**：
```css
/* 桌面端 */
border-right: 1px solid var(--token-border-light);

/* 移动端 */
border-bottom: 1px solid var(--token-border-light);
```

### 决策 6：容器阴影

**选择**：使用 ChatGPT 风格的 `shadow-long` 阴影。

**样式定义**：
```css
box-shadow: 
  0px 8px 12px 0px rgba(0, 0, 0, 0.08),
  0px 0px 1px 0px rgba(0, 0, 0, 0.62);
```

**理由**：
- 更柔和、更有层次的阴影效果
- 与 ChatGPT 视觉风格一致

## 风险 / 权衡

| 风险 | 缓解措施 |
|------|----------|
| 移动端导航项过多导致水平滚动体验不佳 | 设置最小宽度，添加渐变遮罩提示可滚动 |
| 内容区高度固定可能不够 | 设置 `max-h-[85vh]` 并允许滚动 |
