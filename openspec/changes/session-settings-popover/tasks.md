## 1. SessionSettings 组件重构

- [x] 1.1 将 SessionSettings 从面板改为弹出组件结构
- [x] 1.2 添加 useOnClickOutside hook 处理点击外部关闭
- [x] 1.3 实现相对于触发按钮的定位逻辑
- [x] 1.4 添加未保存更改提示逻辑

## 2. 样式优化

- [x] 2.1 应用 SettingsPage 风格（圆角 16px、阴影、背景变量）
- [x] 2.2 设置面板尺寸（宽度 400px、最大高度 500px、响应式适配）
- [x] 2.3 实现内部滚动布局
- [x] 2.4 实现标题栏样式（与 Section Header 一致）
- [x] 2.5 优化分隔线样式

## 3. ToolSettings 样式适配

- [x] 3.1 将 ToolSettings 硬编码颜色替换为 CSS 变量
- [x] 3.2 测试 ToolSettings 在新面板中的显示效果

## 4. App.tsx 集成

- [x] 4.1 移除右侧固定面板布局代码
- [x] 4.2 修改设置按钮点击逻辑为切换 popover
- [x] 4.3 添加 popover 渲染条件

## 5. 验证测试

- [x] 5.1 测试点击按钮打开/关闭面板
- [x] 5.2 测试点击外部关闭面板
- [x] 5.3 测试未保存更改提示
- [x] 5.4 测试小屏幕适配
