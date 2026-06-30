## 为什么

当前设置页面使用水平顶部标签页布局，与 ChatGPT 的垂直左侧导航风格不一致。用户界面整体采用 ChatGPT 风格设计，但设置页面布局的差异造成视觉断层，影响用户体验的一致性。

## 变更内容

重构 `SettingsPage.tsx` 组件，采用 ChatGPT 风格的设置页面布局：
- 将水平标签页改为垂直左侧导航栏
- 左右分栏布局（导航 + 内容区）
- 导航项使用 `__menu-item` 样式，带图标和圆角背景高亮
- 移动端响应式：导航变为水平滚动条
- 调整容器尺寸为 680px × 420px
- 关闭按钮移至左侧导航栏顶部

## 功能 (Capabilities)

### 新增功能

（无新增功能）

### 修改功能

- `settings-page`: 重构设置页面布局为 ChatGPT 风格的垂直左侧导航 + 右侧内容区分栏布局

## 影响

- `frontend/src/components/settings/SettingsPage.tsx` - 主要修改文件
- `frontend/src/index.css` - 可能需要添加 `__menu-item` 相关样式
